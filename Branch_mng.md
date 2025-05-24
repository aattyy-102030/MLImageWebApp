# ブランチ管理
## develop ブランチ
```
/MLImageWebApp (develop ブランチの内容)
├── .github/                     # GitHub ActionsなどのCI/CD設定 (開発用CIなど)
│   └── workflows/
│       └── main.yml
│
├── frontend/
│   ├── app.py                   # Streamlitのメインアプリケーション (開発中の変更を含む)
│   ├── requirements.txt         # StreamlitアプリケーションのPython依存関係 (開発中の依存関係を含む)
│   ├── .streamlit/              # Streamlitの設定ファイル (開発用設定を含む場合あり)
│   │   └── config.toml
│   └── Dockerfile               # Streamlitアプリケーション用のDockerfile (開発用)
│
├── backend/
│   ├── inference_lambda/
│   │   ├── lambda_function.py   # Lambdaハンドラコード (開発中の変更を含む)
│   │   ├── requirements.txt     # Lambda関数のPython依存関係 (開発中の依存関係を含む)
│   │   └── Dockerfile           # (Optional) Lambdaコンテナイメージ用Dockerfile (開発用)
│   ├── model_update_lambda/     # モデル更新ロジック関連のLambda関数など (開発中の変更を含む)
│   │   └── ...
│   └── common/                  # バックエンド共通のPythonモジュールなど (開発中の変更を含む)
│       └── utils.py
│
├── models/                      # 学習済みモデルファイル（開発用、通常は.gitignoreで除外）
│   └── (model_files.h5, .pb など)
│
├── infra/                       # AWSインフラストラクチャ定義 (開発/ステージング環境用の設定を含む場合あり)
│   ├── main.tf                  # Terraformの場合
│   └── (その他設定ファイル)
│
├── data/                        # 学習データ、テストデータなど（通常は.gitignoreで除外）
│   └── (sample_images/, annotations/ など)
│
├── .env.develop                 # 開発環境用の環境変数 (Optional)
├── .gitignore                   # Gitで管理しないファイルを指定
├── README.md                    # プロジェクトの概要、セットアップ手順、使い方など (開発中の情報を含む)
└── LICENSE                      # ライセンス情報
```
