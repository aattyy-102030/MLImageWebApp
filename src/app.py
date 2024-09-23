import streamlit as st
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import img_to_array

def load_model():
    model = MobileNetV2(weights='imagenet')
    return model

def predict(image, model):
    # 画像をモデルの入力サイズにリサイズ
    image = image.resize((224, 224))
    # 画像をarrayに変換し、前処理を実行
    image = img_to_array(image)
    image = preprocess_input(image)
    image = tf.expand_dims(image, axis=0) # バッチ次元の追加

    # 予測の実行
    preds = model.predict(image)
    # decode_predictions はリストのリストを返すため、最初の結果の最初のタプルを取得.
    top_pred = decode_predictions(preds, top=1)[0][0]
    return (top_pred[1], top_pred[2])   # (label, probabillity)

def main():
    st.title('猫画像認識アプリケーション')

    model = load_model()

    uploaded_file = st.file_uploader("画像をアップロードしてください", type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='アップロードされた画像', use_column_width=True)
        st.write("画像が正常にアップロードされました。")

        # 予測の実行
        label, prob = predict(image, model)
        # st.write(f"予測結果: {label}, 確率: {prob * 100:.2f}%")
        st.markdown(f"<h2 style='text-align: center; font-weight: bold; color: red;'>予測結果: {label}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; color: blue;'>確率: {prob * 100:.2f}%</h3>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
