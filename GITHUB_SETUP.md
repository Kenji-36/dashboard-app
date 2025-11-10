# GitHub連携セットアップガイド

このガイドでは、ローカルのGitリポジトリをGitHubと連携させる手順を説明します。

## 前提条件

✅ Gitがインストール済み
✅ GitHubアカウントを持っている
✅ ローカルリポジトリが初期化済み（完了）
✅ Gitユーザー情報が設定済み（完了）

## ステップ1: GitHubでリポジトリを作成

1. **GitHubにログイン**
   - https://github.com にアクセス
   - ユーザー名: `saablow` でログイン

2. **新規リポジトリを作成**
   - 右上の「+」ボタンをクリック
   - 「New repository」を選択

3. **リポジトリ情報を入力**
   ```
   Repository name: dashboard-app
   Description: Pythonダッシュボードアプリケーション（Streamlit）
   Visibility: Public または Private を選択
   
   ⚠️ 重要: 以下のオプションは全てチェックしない
   □ Add a README file
   □ Add .gitignore
   □ Choose a license
   ```

4. **「Create repository」をクリック**

5. **リポジトリURLをコピー**
   - 作成後に表示されるページで、HTTPSのURLをコピー
   - 形式: `https://github.com/saablow/dashboard-app.git`

## ステップ2: リモートリポジトリを追加

GitHubで作成したリポジトリのURLを使って、以下のコマンドを実行してください：

```bash
# リモートリポジトリを追加（URLは実際のものに置き換えてください）
git remote add origin https://github.com/saablow/dashboard-app.git

# リモートリポジトリが追加されたか確認
git remote -v
```

出力例：
```
origin  https://github.com/saablow/dashboard-app.git (fetch)
origin  https://github.com/saablow/dashboard-app.git (push)
```

## ステップ3: 初回プッシュ

```bash
# masterブランチをGitHubにプッシュ
git push -u origin master
```

初回プッシュ時、GitHubの認証情報を求められる場合があります：

### 認証方法

**方法1: Personal Access Token（推奨）**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 「Generate new token (classic)」をクリック
3. 以下を設定：
   - Note: `Dashboard App`
   - Expiration: 適切な期限を選択
   - Scopes: `repo` にチェック
4. トークンをコピー（一度しか表示されません！）
5. プッシュ時にパスワードの代わりにトークンを入力

**方法2: GitHub CLI（gh）**

```bash
# GitHub CLIをインストール後
gh auth login
```

## ステップ4: 確認

GitHubのリポジトリページをブラウザで開いて、ファイルがアップロードされているか確認してください。

## 今後の作業フロー

### 変更をGitHubにプッシュ

```bash
# 変更をステージング
git add .

# コミット
git commit -m "コミットメッセージ"

# GitHubにプッシュ
git push
```

### GitHubから最新の変更を取得

```bash
# 最新の変更を取得してマージ
git pull
```

## トラブルシューティング

### エラー: "remote origin already exists"

```bash
# 既存のリモートを削除
git remote remove origin

# 再度追加
git remote add origin https://github.com/saablow/dashboard-app.git
```

### エラー: "failed to push some refs"

```bash
# リモートの変更を先に取得
git pull origin master --allow-unrelated-histories

# 再度プッシュ
git push -u origin master
```

### 認証エラー

- パスワード認証は廃止されています
- Personal Access Tokenを使用してください
- または、GitHub CLIを使用してください

## 便利なGitコマンド

```bash
# 現在の状態を確認
git status

# コミット履歴を確認
git log --oneline

# リモートリポジトリの情報を確認
git remote -v

# ブランチ一覧を確認
git branch -a
```

## 次のステップ

1. ✅ .gitignoreファイルの作成（完了）
2. ⏳ GitHubでリポジトリを作成
3. ⏳ リモートリポジトリを追加
4. ⏳ 初回プッシュ
5. ⏳ GitHub Actionsの設定（オプション）
6. ⏳ README.mdの充実化（オプション）

---

**作成日**: 2025-11-09
**対象プロジェクト**: Pythonダッシュボードアプリケーション

