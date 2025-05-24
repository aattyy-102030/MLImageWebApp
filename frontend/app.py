import streamlit as st
from PIL import Image, ImageDraw, ImageFont # Pillowライブラリを使用
import io

# --- ページ設定 ---
st.set_page_config(
    page_title="画像判定Webアプリ (プロトタイプ)",
    page_icon="📸",
    layout="centered" # wide にすると表示領域が広くなります
)

st.title("📸 AI画像判定Webアプリ")
st.markdown("---")

st.write("画像をアップロードしてください。アップロード後、AIが画像を分析し、検出されたオブジェクトをハイライト表示します。")

# --- 画像アップロードセクション ---
uploaded_file = st.file_uploader("画像をアップロード", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 画像をPIL Imageとして読み込み
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)
    st.write("") # スペース

    # プログレスバーの表示（ダミー処理の演出）
    with st.spinner("画像を分析中..."):
        import time
        time.sleep(2) # 2秒間待機

    # --- ダミーの推論結果を生成（実際はLambdaからの結果を処理） ---
    # 例: オブジェクト、信頼度、バウンディングボックスのリスト
    # [x1, y1, x2, y2] はそれぞれ (左上x, 左上y, 右下x, 右下y) の座標
    dummy_detections = [
        {"label": "Dog", "score": 0.95, "box": [50, 100, 200, 300]},
        {"label": "Car", "score": 0.88, "box": [250, 50, 400, 250]},
        {"label": "Person", "score": 0.70, "box": [10, 10, 100, 150]}
    ]

    # 画像に検出結果を描画
    draw = ImageDraw.Draw(image)
    try:
        # デフォルトフォントが利用できない場合のフォールバック
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default() # Fallback to default font

    detected_objects = []
    for det in dummy_detections:
        x1, y1, x2, y2 = det['box']
        label = det['label']
        score = det['score']

        # バウンディングボックスを描画
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

        # ラベルとスコアを描画 (ボックスの左上)
        text_to_display = f"{label} ({score:.2f})"
        text_bbox = draw.textbbox((x1, y1), text_to_display, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # テキスト背景を描画 (見やすくするため)
        draw.rectangle([x1, y1 - text_height - 5, x1 + text_width, y1], fill="red")
        draw.text((x1, y1 - text_height - 5), text_to_display, fill="white", font=font)

        detected_objects.append(f"- {label} (信頼度: {score:.2f})")

    st.subheader("分析結果")
    if detected_objects:
        st.image(image, caption="分析結果 (バウンディングボックス)", use_column_width=True)
        st.write("検出されたオブジェクト:")
        for obj in detected_objects:
            st.write(obj)
    else:
        st.write("画像からオブジェクトは検出されませんでした。")

    st.markdown("---")
    st.success("分析が完了しました！")

else:
    st.info("↑画像をアップロードして開始してください。")

st.markdown("ご質問やフィードバックがあれば、お気軽にお寄せください。")
