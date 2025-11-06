# VC Task Manager Backend

このディレクトリにはFastAPIで実装したベンチャーキャピタリスト向けタスク管理サービスのバックエンドが含まれています。

## セットアップ

Python 3.8 以上が必要です。

1. 依存関係のインストール  
   ```bash
   pip install -r requirements.txt
   ```

2. アプリの起動  
   ```bash
   uvicorn vc_task_manager_backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## デプロイ

Renderにデプロイする際は、`render.yaml` をルートに置いてこのアプリをWebサービスとして作成します。ビルドコマンドは `pip install -r requirements.txt`、スタートコマンドは `uvicorn vc_task_manager_backend.main:app --host 0.0.0.0 --port $PORT` に設定します。

カレンダー連携にはGoogle Calendar APIの認証情報が必要です。`GOOGLE_CALENDAR_CREDENTIALS` 環境変数に認証情報JSONファイルの内容を設定してください。
