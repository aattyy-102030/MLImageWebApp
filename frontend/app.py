import streamlit as st
from PIL import Image
import boto3
import json
import uuid
import io
import requests

# --- 定数（環境に合わせて設定） ---
S3_UPLOAD_BUCKET_NAME = "ytm-ml-image-web-app"
LAMBDA_API_ENDPOINT = "https://z32qp2picj.execute-api.ap-northeast-1.amazonaws.com/default/ImageInferenceFunction"

st.set_page_config(layout="wide")
st.title("画像アップロード＆分析アプリ")

# --- 画像アップロードセクション ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # --- デバッグ情報 ---
    # st.write(f"**--- アップロードファイル情報（Streamlit） ---**")
    # st.write(f"ファイル名: {uploaded_file.name}")
    # st.write(f"ファイルタイプ: {uploaded_file.type}")
    # st.write(f"Streamlitが認識したファイルサイズ: {uploaded_file.size} bytes")

    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()

    # st.write(f"メモリに読み込んだバイト配列の長さ: {len(file_bytes)} bytes")

    image_stream_for_pil = io.BytesIO(file_bytes)
    image_stream_for_s3 = io.BytesIO(file_bytes)

    image = None
    try:
        image = Image.open(image_stream_for_pil)
        st.image(image, caption="アップロードされた画像", use_column_width=True)
        st.write(f"PIL Image loaded: Format={image.format}, Size={image.size}, Mode={image.mode}")
    except Exception as e:
        st.error(f"**エラー: PILでの画像表示に失敗しました。ファイルが破損している可能性があります。**")
        st.exception(e)
        st.info("S3へのアップロード前に、すでにファイルがPILで開けない状態です。")
        image = None

    st.write("")

    if image is not None:
        with st.spinner("画像をS3にアップロードし、分析中..."):
            try:
                s3_client = boto3.client('s3',
                                        aws_access_key_id=st.secrets["aws_access_key_id"],
                                        aws_secret_access_key=st.secrets["aws_secret_access_key"])

                file_extension = uploaded_file.name.split('.')[-1]
                s3_key = f"uploads/{uuid.uuid4()}.{file_extension}"

                image_stream_for_s3.seek(0)

                s3_client.upload_fileobj(image_stream_for_s3, S3_UPLOAD_BUCKET_NAME, s3_key)
                # st.success(f"画像をS3にアップロードしました: s3://{S3_UPLOAD_BUCKET_NAME}/{s3_key}")
                # st.write(f"**--- S3アップロード情報 ---**")
                # st.write(f"S3パス: s3://{S3_UPLOAD_BUCKET_NAME}/{s3_key}")
                # st.write(f"S3コンソールでこのファイルを確認してください。ファイルサイズが元のファイルと一致していますか？")

                # --- Lambda関数を呼び出す ---
                payload = {
                    "bucket": S3_UPLOAD_BUCKET_NAME,
                    "key": s3_key
                }
                headers = {'Content-Type': 'application/json'}

                response = requests.post(LAMBDA_API_ENDPOINT, data=json.dumps(payload), headers=headers)

                # Lambdaからの生のレスポンス (デバッグ用)
                # st.write("--- Lambda Response (Raw) ---")
                # st.write(f"Status Code: {response.status_code}")
                # st.write(f"Headers: {response.headers}")
                # st.write(f"Body (Text): {response.text}") # これが上で報告してくれたJSON文字列です
                # st.write("---------------------------")

                processed_image_url = None
                detections = []

                try:
                    # response.json() が直接、{"message": ..., "analysis_results": ...} の形式を返すため
                    # そのまま lambda_response_data に格納
                    lambda_response_data = response.json()
                    st.write("Parsed JSON Response (from response.json()):", lambda_response_data) # ここが、上で報告してくれたJSONです

                    # lambda_response_data がすでに求めているJSON構造そのものであるため、
                    # 直接 analysis_results と message を抽出します
                    if 'analysis_results' in lambda_response_data and isinstance(lambda_response_data['analysis_results'], dict):
                        detections = lambda_response_data['analysis_results'].get('detections', [])
                        processed_image_url = lambda_response_data['analysis_results'].get('processed_image_url')
                        st.write("Successfully extracted detections and URL from 'analysis_results'.")
                    else:
                        st.error("エラー: Lambdaレスポンスに期待される 'analysis_results' キーが見つからないか、形式が不正です。")
                        # 念のため、トップレベルに直接あった場合のフォールバック（今回は不要なはずですが安全のため）
                        detections = lambda_response_data.get('detections', [])
                        processed_image_url = lambda_response_data.get('processed_image_url')

                except json.JSONDecodeError:
                    st.error("エラー: Lambdaレスポンスのトップレベルが有効なJSONではありませんでした。")
                    st.write(f"生のレスポンステキスト: {response.text}")
                except Exception as e:
                    st.error(f"エラー: Lambdaレスポンスの処理中に予期せぬエラーが発生しました: {e}")
                    st.exception(e)

                if response.status_code == 200:
                    st.success("Lambda関数による分析が完了しました！")

                    if processed_image_url:
                        st.subheader("分析結果（ダミー矩形付き）")
                        st.image(processed_image_url, caption="Lambdaで処理された画像", use_column_width=True)
                        st.write(f"画像URL: {processed_image_url}")
                    else:
                        st.warning("処理済み画像のURLがLambdaから返されませんでした。")

                    if detections:
                        st.subheader("ダミー検出結果（JSON）")
                        st.json(detections)
                    else:
                        st.info("ダミーの検出結果はありませんでした。")

                else:
                    st.error(f"Lambda関数でエラーが発生しました (Status: {response.status_code}): {lambda_response_data.get('message', 'No error message from Lambda')}") # エラーメッセージの取得元も修正
                    detections = []

            except requests.exceptions.RequestException as e:
                st.error(f"Lambda関数の呼び出し中にエラーが発生しました: {e}")
                detections = []
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")
                detections = []
    else:
        st.error("アップロードされた画像の読み込みに失敗したため、S3へのアップロードとLambda分析はスキップされました。")
