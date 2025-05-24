import streamlit as st
from PIL import Image, ImageDraw, ImageFont # Pillowライブラリを使用
import io
import requests
import json
import boto3

# --- ページ設定 ---
st.set_page_config(
    page_title="画像判定Webアプリ (プロトタイプ)",
    page_icon="📸",
    layout="centered" # wide にすると表示領域が広くなります
)

st.title("📸 AI画像判定Webアプリ")
st.markdown("---")

st.write("画像をアップロードしてください。アップロード後、AIが画像を分析し、検出されたオブジェクトをハイライト表示します。")


# ★★★ ここをあなたのAPI GatewayエンドポイントURLに置き換えてください ★★★
# 例: "https://abcdef123.execute-api.ap-northeast-1.amazonaws.com/default/ImageInferenceFunction"
LAMBDA_API_ENDPOINT = "https://z32qp2picj.execute-api.ap-northeast-1.amazonaws.com/default/ImageInferenceFunction"

# ★★★ ここをあなたのS3バケット名に置き換えてください ★★★
S3_UPLOAD_BUCKET_NAME = "ytm-ml-image-web-app"


# --- 画像アップロードセクション ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 画像をPIL Imageとして読み込み
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)
    st.write("") # スペース

    # プログレスバーの表示
    with st.spinner("画像をS3にアップロードし、分析中..."):
        try:
            # --- 画像をS3にアップロード ---
            s3_client = boto3.client('s3',
                                    aws_access_key_id=st.secrets["aws_access_key_id"],
                                    aws_secret_access_key=st.secrets["aws_secret_access_key"])

            # S3に保存するファイル名（例: UUID + 拡張子など、一意になるように）
            import uuid
            file_extension = uploaded_file.name.split('.')[-1]
            s3_key = f"uploads/{uuid.uuid4()}.{file_extension}"

            s3_client.upload_fileobj(uploaded_file, S3_UPLOAD_BUCKET_NAME, s3_key)
            st.success(f"画像をS3にアップロードしました: s3://{S3_UPLOAD_BUCKET_NAME}/{s3_key}")

            # --- Lambda関数を呼び出す ---
            payload = {
                "bucket": S3_UPLOAD_BUCKET_NAME,
                "key": s3_key
            }
            headers = {'Content-Type': 'application/json'}

            response = requests.post(LAMBDA_API_ENDPOINT, data=json.dumps(payload), headers=headers)
            response.raise_for_status() # HTTPエラーが発生した場合に例外を発生させる

            lambda_response = response.json()
            # Lambdaの戻り値は 'body' の中にJSON文字列として入っているので、さらにパース
            inference_results = json.loads(lambda_response.get('body', '{}'))

            # 推論結果を抽出 (lambda_function.pyの 'detections' キーに合わせる)
            detections = inference_results.get('detections', [])

            st.success("Lambda関数による分析が完了しました！")

        except requests.exceptions.RequestException as e:
            st.error(f"Lambda関数の呼び出し中にエラーが発生しました: {e}")
            detections = [] # エラー時は検出なしとする
        except Exception as e:
            st.error(f"S3アップロードまたは処理中に予期せぬエラーが発生しました: {e}")
            detections = []

    # --- 検出結果を描画 ---
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    detected_objects_summary = []
    if detections:
        for det in detections: # Lambdaからの結果を使用
            x1, y1, x2, y2 = det['box']
            label = det['label']
            score = det['score']

            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

            text_to_display = f"{label} ({score:.2f})"
            text_bbox = draw.textbbox((x1, y1), text_to_display, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            draw.rectangle([x1, y1 - text_height - 5, x1 + text_width, y1], fill="red")
            draw.text((x1, y1 - text_height - 5), text_to_display, fill="white", font=font)

            detected_objects_summary.append(f"- {label} (信頼度: {score:.2f})")

        st.subheader("分析結果")
        st.image(image, caption="分析結果 (バウンディングボックス)", use_column_width=True)
        st.write("検出されたオブジェクト:")
        for obj in detected_objects_summary:
            st.write(obj)
    else:
        st.write("画像からオブジェクトは検出されませんでした。")
        if not detections and uploaded_file is not None:
            st.info("※エラーメッセージが表示されていない場合、これはLambdaから検出結果が0件と返されたことを意味します。")


    st.markdown("---")
    # st.success("分析が完了しました！") # 既に上に移動したのでコメントアウト

else:
    st.info("↑画像をアップロードして開始してください。")

st.markdown("ご質問やフィードバックがあれば、お気軽にお寄せください。")
