# ブランチ管理
## main ブランチ
```
/MLImageWebApp (main ブランチの内容)
├── frontend/
│   ├── app.py                   # Streamlitのメインアプリケーション
│   ├── requirements.txt         # StreamlitアプリケーションのPython依存関係
│   ├── .streamlit/              # Streamlitの設定ファイル (本番用)
│   │   └── config.toml
│   └── Dockerfile               # Streamlitアプリケーション用のDockerfile (本番用)
│
├── backend/
│   ├── inference_lambda/
│   │   ├── lambda_function.py   # Lambdaハンドラコード
│   │   ├── requirements.txt     # Lambda関数のPython依存関係
│   │   └── Dockerfile           # (Optional) Lambdaコンテナイメージ用Dockerfile (本番用)
│   └── common/                  # バックエンド共通のPythonモジュールなど (本番用)
│       └── utils.py
│
├── .gitignore                   # Gitで管理しないファイルを指定
├── README.md                    # プロジェクトの概要、セットアップ手順、使い方など
└── LICENSE                      # ライセンス情報
```
