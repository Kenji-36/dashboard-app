# デプロイメントガイド

## 📦 Phase 4 ダッシュボードのデプロイ方法

このドキュメントでは、Phase 4ダッシュボードを様々な環境にデプロイする方法を説明します。

---

## 目次

1. [ローカル環境](#ローカル環境)
2. [Docker](#docker)
3. [Streamlit Cloud](#streamlit-cloud)
4. [AWS](#aws)
5. [Azure](#azure)
6. [Google Cloud Platform](#google-cloud-platform)
7. [Heroku](#heroku)

---

## ローカル環境

### 前提条件

- Python 3.11以上
- pip
- Git

### セットアップ手順

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd ダッシュボード開発

# 2. 仮想環境の作成
python -m venv venv

# 3. 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 依存関係のインストール
pip install -r requirements.txt

# 5. アプリケーションの起動
streamlit run src/pages/1_🏠_Home.py
```

### バッチファイルでの起動（Windows）

```bash
# Phase 4の起動
run_phase4.bat
```

---

## Docker

### 前提条件

- Docker Desktop
- Docker Compose

### ビルドと起動

```bash
# 1. Dockerイメージのビルド
docker-compose -f docker/docker-compose.yml build

# 2. コンテナの起動
docker-compose -f docker/docker-compose.yml up -d

# 3. ログの確認
docker-compose -f docker/docker-compose.yml logs -f

# 4. コンテナの停止
docker-compose -f docker/docker-compose.yml down
```

### 個別のDockerコマンド

```bash
# イメージのビルド
docker build -t sales-dashboard:phase4 -f docker/Dockerfile .

# コンテナの起動
docker run -d \
  --name sales-dashboard \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  sales-dashboard:phase4

# コンテナの停止
docker stop sales-dashboard

# コンテナの削除
docker rm sales-dashboard
```

### ブラウザでアクセス

```
http://localhost:8501
```

---

## Streamlit Cloud

### 前提条件

- GitHubアカウント
- Streamlit Cloudアカウント

### デプロイ手順

1. **GitHubにプッシュ**

```bash
git add .
git commit -m "Phase 4 deployment"
git push origin main
```

2. **Streamlit Cloudでデプロイ**

- [Streamlit Cloud](https://streamlit.io/cloud) にログイン
- "New app" をクリック
- リポジトリを選択
- メインファイルパス: `src/pages/1_🏠_Home.py`
- "Deploy" をクリック

3. **環境変数の設定**（必要に応じて）

Settings → Secrets で環境変数を設定

```toml
# .streamlit/secrets.toml
[database]
host = "your-db-host"
port = 5432
database = "your-db-name"
user = "your-db-user"
password = "your-db-password"
```

---

## AWS

### AWS EC2でのデプロイ

#### 1. EC2インスタンスの作成

- AMI: Ubuntu 22.04 LTS
- インスタンスタイプ: t2.medium以上
- セキュリティグループ: ポート8501を開放

#### 2. インスタンスへの接続

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### 3. 環境のセットアップ

```bash
# システムの更新
sudo apt update && sudo apt upgrade -y

# Pythonのインストール
sudo apt install python3.11 python3.11-venv python3-pip -y

# Gitのインストール
sudo apt install git -y

# リポジトリのクローン
git clone <repository-url>
cd ダッシュボード開発

# 仮想環境の作成とアクティベート
python3.11 -m venv venv
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

#### 4. Systemdサービスの作成

```bash
sudo nano /etc/systemd/system/dashboard.service
```

```ini
[Unit]
Description=Sales Dashboard Phase 4
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ダッシュボード開発
Environment="PATH=/home/ubuntu/ダッシュボード開発/venv/bin"
ExecStart=/home/ubuntu/ダッシュボード開発/venv/bin/streamlit run src/pages/1_🏠_Home.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5. サービスの起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
sudo systemctl status dashboard
```

#### 6. Nginxのリバースプロキシ設定（オプション）

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/dashboard
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### AWS ECS（Elastic Container Service）

#### 1. ECRにイメージをプッシュ

```bash
# ECRリポジトリの作成
aws ecr create-repository --repository-name sales-dashboard

# ECRにログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com

# イメージのビルドとタグ付け
docker build -t sales-dashboard:phase4 -f docker/Dockerfile .
docker tag sales-dashboard:phase4 <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/sales-dashboard:latest

# イメージのプッシュ
docker push <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/sales-dashboard:latest
```

#### 2. ECSタスク定義の作成

AWS Management Console → ECS → Task Definitions → Create new Task Definition

#### 3. ECSサービスの作成

AWS Management Console → ECS → Clusters → Create Service

---

## Azure

### Azure App Service

#### 1. Azure CLIのインストール

```bash
# macOS
brew install azure-cli

# Windows
# https://aka.ms/installazurecliwindows からインストーラーをダウンロード
```

#### 2. Azureにログイン

```bash
az login
```

#### 3. リソースグループの作成

```bash
az group create --name dashboard-rg --location japaneast
```

#### 4. App Serviceプランの作成

```bash
az appservice plan create \
  --name dashboard-plan \
  --resource-group dashboard-rg \
  --sku B1 \
  --is-linux
```

#### 5. Web Appの作成

```bash
az webapp create \
  --resource-group dashboard-rg \
  --plan dashboard-plan \
  --name sales-dashboard-phase4 \
  --runtime "PYTHON:3.11"
```

#### 6. デプロイ

```bash
# ZIPデプロイ
zip -r app.zip . -x "venv/*" ".git/*"
az webapp deployment source config-zip \
  --resource-group dashboard-rg \
  --name sales-dashboard-phase4 \
  --src app.zip
```

---

## Google Cloud Platform

### Cloud Run

#### 1. gcloud CLIのインストール

```bash
# https://cloud.google.com/sdk/docs/install からインストール
```

#### 2. プロジェクトの設定

```bash
gcloud init
gcloud config set project your-project-id
```

#### 3. Container Registryへのプッシュ

```bash
# イメージのビルド
docker build -t gcr.io/your-project-id/sales-dashboard:phase4 -f docker/Dockerfile .

# 認証
gcloud auth configure-docker

# イメージのプッシュ
docker push gcr.io/your-project-id/sales-dashboard:phase4
```

#### 4. Cloud Runへのデプロイ

```bash
gcloud run deploy sales-dashboard \
  --image gcr.io/your-project-id/sales-dashboard:phase4 \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 8501
```

---

## Heroku

### 前提条件

- Herokuアカウント
- Heroku CLI

### デプロイ手順

#### 1. Heroku CLIのインストール

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# https://devcenter.heroku.com/articles/heroku-cli からインストーラーをダウンロード
```

#### 2. Herokuにログイン

```bash
heroku login
```

#### 3. アプリの作成

```bash
heroku create sales-dashboard-phase4
```

#### 4. 必要なファイルの作成

**Procfile:**
```
web: streamlit run src/pages/1_🏠_Home.py --server.port=$PORT --server.address=0.0.0.0
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### 5. デプロイ

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### 6. アプリを開く

```bash
heroku open
```

---

## 環境変数の設定

### .env ファイルの例

```bash
# データベース設定
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_db
DB_USER=dashboard_user
DB_PASSWORD=secure_password

# API設定
API_KEY=your-api-key
API_SECRET=your-api-secret

# アプリケーション設定
DEBUG=False
LOG_LEVEL=INFO
CACHE_TTL=300
```

### Streamlit Secrets

`.streamlit/secrets.toml`:
```toml
[database]
host = "localhost"
port = 5432
database = "sales_db"
user = "dashboard_user"
password = "secure_password"

[api]
key = "your-api-key"
secret = "your-api-secret"
```

---

## 監視とログ

### ログの確認

```bash
# Docker
docker logs sales-dashboard

# Systemd
sudo journalctl -u dashboard -f

# Heroku
heroku logs --tail

# AWS CloudWatch
aws logs tail /aws/ecs/sales-dashboard --follow
```

### ヘルスチェック

```bash
# ローカル
curl http://localhost:8501/_stcore/health

# リモート
curl https://your-domain.com/_stcore/health
```

---

## トラブルシューティング

### ポートが使用中

```bash
# Windowsでポートを確認
netstat -ano | findstr :8501

# プロセスを終了
taskkill /PID <PID> /F

# macOS/Linuxでポートを確認
lsof -i :8501

# プロセスを終了
kill -9 <PID>
```

### メモリ不足

- インスタンスサイズを増やす
- データのフィルタリングを活用
- キャッシュ設定を最適化

### 接続エラー

- ファイアウォール設定を確認
- セキュリティグループを確認
- ポートが正しく開放されているか確認

---

## セキュリティのベストプラクティス

1. **HTTPS の使用**: Let's Encrypt で SSL証明書を取得
2. **環境変数**: 機密情報は環境変数で管理
3. **ファイアウォール**: 必要なポートのみ開放
4. **定期更新**: 依存パッケージを定期的に更新
5. **バックアップ**: データの定期的なバックアップ

---

## パフォーマンス最適化

1. **キャッシング**: `@st.cache_data` を活用
2. **CDN**: 静的ファイルはCDNから配信
3. **データベース**: インデックスを適切に設定
4. **圧縮**: gzip圧縮を有効化
5. **ロードバランシング**: 複数インスタンスで負荷分散

---

## サポート

デプロイに関する質問や問題がある場合は、以下を参照してください：

- **ドキュメント**: README_Phase4.md
- **FAQ**: ヘルプページ
- **GitHub Issues**: バグ報告・機能リクエスト
- **メール**: support@dashboard-analytics.com

---

**Phase 4 ダッシュボード** | デプロイメントガイド v1.0

