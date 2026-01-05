# 日経平均株価自動ツイートBot

日経平均株価の価格変動を検知し、その情報を自動的にX (旧Twitter) にツイートするBotです。GitHub Actionsを利用して自動実行され、必要なAPIキーはGitHubの環境変数として管理されます。

## 機能概要

-   **日経平均株価の監視**: Yahoo Financeから`yfinance`ライブラリを使用して日経平均株価のデータを定期的に取得します。
-   **価格変動の検知**: 前日終値と比較し、設定された閾値（デフォルトは±1%）以上の変動があった場合にツイートを生成します。
-   **ツイート生成**: Google Gemini APIを利用して、変動情報に基づいた自然なツイート文を生成します。
-   **自動ツイート**: 生成されたツイートをX (旧Twitter) に自動投稿します。
-   **GitHub Actionsによる自動化**: 定期的な株価チェックとツイート投稿はGitHub Actionsによって自動実行されます。

## 要件定義

### トリガーと変動の定義

-   **トリガー**: 日経平均株価の価格変動。
-   **価格変動の定義**: 前日比±0.3%以上の変動を検知した場合にツイートを生成します。この閾値は`src/main.py`内の`THRESHOLD_PERCENT`変数を変更することで調整可能です。

### ツイート内容

以下の情報要素をツイートに含めます。

-   銘柄: 日経平均株価
-   現在の価格
-   変動方向（上昇/下落）
-   変動幅（円）
-   変動率（%）
-   データ取得時の日時（日本時間）
-   ハッシュタグ: `#日経平均`, `#株価変動`, `#投資`

### ツイート例

-   「日経平均株価が上昇しました📈 現在価格: 〇〇円 (前日比 +〇〇円, +〇〇%)。〇月〇日 〇時〇分 #日経平均 #株価変動 #投資」
-   「日経平均株価が下落しました📉 現在価格: 〇〇円 (前日比 -〇〇円, -〇〇%)。〇月〇日 〇時〇分 #日経平均 #株価変動 #投資」

## セットアップ方法

### 1. GitHubリポジトリのクローン

```bash
git clone https://github.com/tomoto0/nikkei-bot.git
cd nikkei-bot
```

### 2. APIキーの取得

以下のサービスからAPIキーとアクセストークンを取得してください。

-   **Google Gemini API**: [Google AI Studio](https://aistudio.google.com/app/apikey) からAPIキーを取得します。
-   **X (旧Twitter) API**: [X Developer Platform](https://developer.twitter.com/en/portal/dashboard) からDeveloper Accountを作成し、APIキー、APIキーシークレット、アクセストークン、アクセストークンシークレットを取得します。

### 3. GitHub Secretsの設定

取得したAPIキーとアクセストークンをGitHubリポジトリのSecretsに設定します。

1.  GitHubリポジトリのページにアクセスします。
2.  `Settings` タブをクリックします。
3.  左側のメニューから `Secrets and variables` -> `Actions` を選択します。
4.  `New repository secret` ボタンをクリックし、以下のシークレットを追加します。
    -   `GEMINI_API_KEY`: Google Gemini APIキー
    -   `X_API_KEY`: X APIキー
    -   `X_API_KEY_SECRET`: X APIキーシークレット
    -   `X_ACCESS_TOKEN`: Xアクセストークン
    -   `X_ACCESS_TOKEN_SECRET`: Xアクセストークンシークレット

### 4. GitHub Actionsワークフロー

ワークフローは`.github/workflows/main.yml`に定義されています。このワークフローは、平日の日本時間午前7時から午後9時まで、3時間ごとに実行されるように設定されています。また、手動で実行することも可能です。

## 開発環境

-   Python 3.9+
-   `yfinance`
-   `google-generativeai`
-   `tweepy`
-   `python-dotenv` (ローカルテスト用)

## ローカルでのテスト実行 (オプション)

1.  **Python環境のセットアップ**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  `.env`ファイルを作成し、APIキーを設定します。
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    X_API_KEY=YOUR_X_API_KEY
    X_API_KEY_SECRET=YOUR_X_API_KEY_SECRET
    X_ACCESS_TOKEN=YOUR_X_ACCESS_TOKEN
    X_ACCESS_TOKEN_SECRET=YOUR_X_ACCESS_TOKEN_SECRET
    ```
3.  スクリプトを実行します。
    ```bash
    python src/main.py
    ```

## 貢献

バグ報告や機能改善の提案は、GitHubのIssueまたはPull Requestでお待ちしております。

## ライセンス

[LICENSE](LICENSE) (必要に応じて追加してください)

## 著者

Tomoto Masuda

