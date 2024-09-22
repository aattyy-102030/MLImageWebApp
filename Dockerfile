# ベースイメージとしてPython 3.8を使用
FROM python:3.8-slim

# 作業ディレクトリを設定
WORKDIR /src

# 必要なパッケージやライブラリをインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースをコンテナ内にコピー
COPY . /src

# Streamlitの実行コマンド
CMD ["streamlit", "run", "your_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
