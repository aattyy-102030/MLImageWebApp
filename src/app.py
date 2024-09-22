import streamlit as st
from PIL import Image

def main():
    st.title('猫画像認識アプリケーション')

    uploaded_file = st.file_uploader("画像をアップロードしてください", type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='アップロードされた画像', use_column_width=True)
        st.write("画像が正常にアップロードされました。")

        # ここで画像処理やモデル予測を行う
        # 例: result = model.predict(image)
        # st.write(f"予測結果: {result}")

if __name__ == '__main__':
    main()
