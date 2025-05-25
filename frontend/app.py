import streamlit as st
from PIL import Image
import boto3
import json
import uuid
import io
import requests # requestsモジュールをインポート

# --- 定数（環境に合わせて設定） ---
S3_UPLOAD_BUCKET_NAME = "ytm-ml-image-web-app"
LAMBDA_API_ENDPOINT = "https://z32qp2picj.execute-api.ap-northeast-1.amazonaws.com/default/ImageInferenceFunction"

st.set_page_config(layout="wide")
st.title("画像アップロード＆分析アプリ")

# --- 画像アップロードセクション ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.write(f"**--- アップロードファイル情報（Streamlit） ---**")
    st.write(f"ファイル名: {uploaded_file.name}")
    st.write(f"ファイルタイプ: {uploaded_file.type}")
    st.write(f"Streamlitが認識したファイルサイズ: {uploaded_file.size} bytes") # Streamlitが提供するファイルサイズ属性

    # uploaded_file オブジェクトのポインタを先頭にリセット (念のため)
    uploaded_file.seek(0)
    # ファイルの全コンテンツを一度に読み込む
    file_bytes = uploaded_file.read()

    st.write(f"メモリに読み込んだバイト配列の長さ: {len(file_bytes)} bytes") # len() で実際に読み込んだバイト数を確認

    # PILでの表示用とS3アップロード用に、それぞれ新しいBytesIOストリームを作成
    image_stream_for_pil = io.BytesIO(file_bytes)
    image_stream_for_s3 = io.BytesIO(file_bytes)

    # 画像をPIL Imageとして読み込み、Streamlitに表示
    # ここで失敗する場合は、既に読み込み段階で問題がある可能性が高い
    image = None # 初期化
    try:
        image = Image.open(image_stream_for_pil)
        st.image(image, caption="アップロードされた画像", use_column_width=True)
        st.write(f"PIL Image loaded: Format={image.format}, Size={image.size}, Mode={image.mode}")
    except Exception as e:
        st.error(f"**エラー: PILでの画像表示に失敗しました。ファイルが破損している可能性があります。**")
        st.exception(e) # 例外の詳細も表示
        st.info("S3へのアップロード前に、すでにファイルがPILで開けない状態です。")
        image = None # エラーが発生したらimageをNoneにする

    st.write("") # スペース

    # プログレスバーの表示
    if image is not None: # PILで画像が正常に読み込めた場合のみS3アップロードと分析に進む
        with st.spinner("画像をS3にアップロードし、分析中..."):
            try:
                # --- 画像をS3にアップロード ---
                s3_client = boto3.client('s3',
                                        aws_access_key_id=st.secrets["aws_access_key_id"],
                                        aws_secret_access_key=st.secrets["aws_secret_access_key"])

                file_extension = uploaded_file.name.split('.')[-1]
                s3_key = f"uploads/{uuid.uuid4()}.{file_extension}"

                # S3アップロード用のストリームのポインタを先頭にリセット (念のため)
                image_stream_for_s3.seek(0)

                s3_client.upload_fileobj(image_stream_for_s3, S3_UPLOAD_BUCKET_NAME, s3_key)
                st.success(f"画像をS3にアップロードしました: s3://{S3_UPLOAD_BUCKET_NAME}/{s3_key}")
                st.write(f"**--- S3アップロード情報 ---**")
                st.write(f"S3パス: s3://{S3_UPLOAD_BUCKET_NAME}/{s3_key}")
                st.write(f"S3コンソールでこのファイルを確認してください。ファイルサイズが元のファイルと一致していますか？")

                # --- Lambda関数を呼び出す ---
                payload = {
                    "bucket": S3_UPLOAD_BUCKET_NAME,
                    "key": s3_key
                }
                headers = {'Content-Type': 'application/json'}

                response = requests.post(LAMBDA_API_ENDPOINT, data=json.dumps(payload), headers=headers)

                # Lambdaからの生のレスポンス (デバッグ用)
                st.write("--- Lambda Response (Raw) ---")
                st.write(f"Status Code: {response.status_code}")
                st.write(f"Headers: {response.headers}")
                st.write(f"Body (Text): {response.text}")
                st.write("---------------------------")

                lambda_response_data = {}
                try:
                    lambda_response_data = response.json()
                    st.write("Parsed JSON Response:", lambda_response_data)
                except json.JSONDecodeError:
                    st.error("Lambda response was not valid JSON.")
                    st.write(f"Raw response text: {response.text}")

                inference_results = {}
                if 'body' in lambda_response_data and isinstance(lambda_response_data['body'], str):
                    try:
                        inference_results = json.loads(lambda_response_data['body'])
                        st.write("Parsed Inference Results:", inference_results)
                    except json.JSONDecodeError:
                        st.error("Lambda response body was not valid JSON string.")
                        inference_results = {}
                elif 'body' in lambda_response_data:
                    st.error("Lambda response 'body' was not a string. It might be already parsed or invalid.")
                    inference_results = lambda_response_data.get('body', {})

                detections = inference_results.get('detections', [])

                if response.status_code == 200:
                    st.success("Lambda関数による分析が完了しました！")
                    st.write("分析結果:", detections)
                else:
                    st.error(f"Lambda関数でエラーが発生しました (Status: {response.status_code}): {lambda_response_data.get('body', 'No error message from Lambda')}")
                    detections = []

            except requests.exceptions.RequestException as e:
                st.error(f"Lambda関数の呼び出し中にエラーが発生しました: {e}")
                detections = []
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")
                detections = []
    else: # if image is None due to PIL error during local display attempt
        st.error("アップロードされた画像の読み込みに失敗したため、S3へのアップロードとLambda分析はスキップされました。")
