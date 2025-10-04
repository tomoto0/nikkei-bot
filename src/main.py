
import os
import yfinance as yf
import tweepy
import google.generativeai as genai
from datetime import datetime, timedelta
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 環境変数からAPIキーを取得
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
X_API_KEY = os.getenv('X_API_KEY')
X_API_KEY_SECRET = os.getenv('X_API_KEY_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')

# Gemini APIの設定
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-pro') # gemini-2.5-pro # gemini-2.5-flash-lite
else:
    logging.error("GEMINI_API_KEYが設定されていません。")
    exit(1)

# X APIの設定
if X_API_KEY and X_API_KEY_SECRET and X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET:
    # API v1.1 の認証
    auth = tweepy.OAuthHandler(X_API_KEY, X_API_KEY_SECRET)
    auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    # API v2 のクライアントは使用しないため、コメントアウトまたは削除
    # client_v2 = tweepy.Client(consumer_key=X_API_KEY, consumer_secret=X_API_KEY_SECRET,
    #                         access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_TOKEN_SECRET)

else:
    logging.error("X APIの認証情報が設定されていません。")
    exit(1)

def get_nikkei_data():
    """Yahoo Financeから日経平均株価データを取得する"""
    ticker = '^N225'
    # 過去2日間のデータを取得（前日終値と比較するため）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5) # 週末や祝日を考慮して少し長めに取得
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            logging.warning("日経平均株価データが取得できませんでした。")
            return None, None
        
        # 最新の終値と前日の終値を取得
        latest_close = df["Close"].iloc[-1].item()
        # 営業日ベースで前日の終値を探す
        if len(df) < 2:
            logging.warning("比較できる前日データがありません。")
            return None, None
        
        previous_close = df["Close"].iloc[-2].item()
        
        return latest_close, previous_close
    except Exception as e:
        logging.error(f"日経平均株価データの取得中にエラーが発生しました: {e}")
        return None, None

def generate_tweet_text(current_price, change_amount, change_percent, direction):
    """Gemini APIを使用してツイートテキストを生成する"""
    prompt = f"""
    日経平均株価の変動についてツイートを作成してください。
    現在の価格: {current_price:.2f}円
    変動額: {change_amount:.2f}円
    変動率: {change_percent:.2f}%
    変動方向: {direction}
    
    以下の要件を満たしてください:
    - 簡潔にまとめる。
    - 感情を示す絵文字を適切に使う。
    - 関連するハッシュタグ（#日経平均 #株価変動 #投資）を含める。
    - 例: 「日経平均株価が上昇しました📈 現在価格: 〇〇円 (前日比 +〇〇円, +〇〇%)。〇月〇日 〇時〇分 #日経平均 #株価変動 #投資」
    """
    
    try:
        response = model.generate_content(prompt)
        tweet_text = response.text.strip()
        # 日付と時刻を追加
        now = datetime.now()
        tweet_text += f" {now.strftime('%m月%d日 %H時%M分')}"
        return tweet_text
    except Exception as e:
        logging.error(f"ツイートテキストの生成中にエラーが発生しました: {e}")
        return None

def post_tweet(text):
    """X (旧Twitter) にツイートを投稿する"""
    try:
        api_v1.update_status(text)

        logging.info(f"ツイートを投稿しました: {text}")
        return True
    except tweepy.TweepyException as e:
        logging.error(f"ツイートの投稿中にエラーが発生しました: {e}")
        return False

def main():
    logging.info("日経平均株価Botを開始します。")
    current_price, previous_close = get_nikkei_data()

    if current_price is None or previous_close is None:
        logging.error("株価データの取得に失敗したため、処理を終了します。")
        return

    logging.info(f"現在の終値: {current_price:.2f}円, 前日の終値: {previous_close:.2f}円")

    change_amount = current_price - previous_close
    change_percent = (change_amount / previous_close) * 100

    # 変動率の閾値 (例: ±1%)
    THRESHOLD_PERCENT = 1.0

    if abs(change_percent) >= THRESHOLD_PERCENT:
        direction = "上昇" if change_amount > 0 else "下落"
        logging.info(f"日経平均株価が{direction}しました。変動率: {change_percent:.2f}%")
        
        tweet_text = generate_tweet_text(current_price, change_amount, change_percent, direction)
        if tweet_text:
            post_tweet(tweet_text)
        else:
            logging.error("ツイートテキストの生成に失敗したため、ツイートを投稿できませんでした。")
    else:
        logging.info(f"日経平均株価の変動は{THRESHOLD_PERCENT}%未満です。ツイートはしません。")

if __name__ == '__main__':
    main()

