# 販売データダッシュボード

Streamlitを使用した販売データの可視化ダッシュボードです。

## 環境構築

### 1. 仮想環境の作成（すでに完了）
```bash
python -m venv venv
```

### 2. 仮想環境のアクティベート

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

### 3. 必要なライブラリのインストール（すでに完了）
```bash
pip install -r requirements.txt
```

## アプリケーションの起動

### 方法1: バッチファイルで起動（最も簡単）

`run_dashboard.bat` をダブルクリックするだけで起動できます。

### 方法2: コマンドラインから起動

仮想環境をアクティベートした状態で、以下のコマンドを実行してください：

```bash
streamlit run app.py
```

### 方法3: 仮想環境をアクティベートせずに起動

**Windows (PowerShell):**
```powershell
venv\Scripts\python.exe -m streamlit run app.py
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\python.exe -m streamlit run app.py
```

ブラウザが自動的に開き、ダッシュボードが表示されます。
デフォルトでは `http://localhost:8501` でアクセスできます。

## 機能

### 📊 ダッシュボード機能

1. **KPI表示**
   - 総売上
   - 平均購入金額
   - 顧客数
   - 平均年齢

2. **フィルター機能**
   - 地域別フィルター
   - 性別フィルター
   - 購入カテゴリー別フィルター

3. **時系列分析**
   - 月別売上推移
   - 支払方法別売上構成
   - 地域別売上

4. **カテゴリー分析**
   - カテゴリー別売上
   - カテゴリー別購入件数

5. **顧客分析**
   - 年齢分布
   - 性別×地域別売上
   - 年齢層別購入金額

6. **データテーブル**
   - カスタマイズ可能な列表示
   - データの並び替え
   - CSVダウンロード機能

## インストール済みライブラリ

- **streamlit**: Webダッシュボードフレームワーク
- **pandas**: データ分析・操作
- **numpy**: 数値計算
- **plotly**: インタラクティブなグラフ作成
- **matplotlib**: グラフ作成
- **seaborn**: 統計的データ可視化
- **openpyxl**: Excelファイル操作
- **pillow**: 画像処理

## データ構造

`data/sample-data.csv`には以下の列が含まれています：

- 顧客ID
- 年齢
- 性別
- 地域
- 購入カテゴリー
- 購入金額
- 購入日
- 支払方法

## トラブルシューティング

### PowerShellでスクリプト実行が拒否される場合

実行ポリシーを変更してください：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ポートが使用中の場合

別のポートを指定して起動：
```bash
streamlit run app.py --server.port 8502
```

## 開発環境

- Python 3.14
- Streamlit 1.50.0
- Windows 10/11

