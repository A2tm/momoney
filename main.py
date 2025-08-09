import os, time, schedule
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST as AlpacaREST
from twilio.rest import Client as TwilioClient
import krakenex
from pykrakenapi import KrakenAPI

load_dotenv()

# === Alpaca Setup ===
APCA_KEY = os.getenv("APCA_API_KEY_ID")
APCA_SECRET = os.getenv("APCA_API_SECRET_KEY")
APCA_URL = os.getenv("APCA_API_BASE_URL")
alpaca = AlpacaREST(APCA_KEY, APCA_SECRET, APCA_URL)

# === Kraken Setup ===
import krakenex
from pykrakenapi import KrakenAPI

kraken = krakenex.API(
    key=os.getenv("KRAKEN_API_KEY"),
    secret=os.getenv("KRAKEN_SECRET_KEY")
)
kraken_api = KrakenAPI(kraken)

# === Twilio Setup ===
twilio_sid = os.getenv("TWILIO_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = TwilioClient(twilio_sid, twilio_token)
FROM = os.getenv("FROM_NUMBER")
TO = os.getenv("TO_NUMBER")

def send_sms(message):
    twilio_client.messages.create(body=message, from_=FROM, to=TO)

# === Trade Logic ===
def trade_stocks():
    symbols = ["AAPL", "TSLA", "META", "AMZN"]
    for symbol in symbols:
        try:
            alpaca.submit_order(symbol=symbol, qty=.2, side="buy", type="market", time_in_force="gtc")
            send_sms(f"STOCK BUY: {symbol}")
        except Exception as e:
            print(f"Alpaca Error: {e}")

def trade_crypto():
    crypto_symbols = ["BTC/USD", "ETH/USD"]
    for pair in crypto_symbols:
        try:
            kraken.query_private('AddOrder', {
                'pair': pair.replace("/", ""),
                'type': 'buy',
                'ordertype': 'market',
                'volume': '0.1'
            })
            send_sms(f"CRYPTO BUY: {pair}")
        except Exception as e:
            print(f"Kraken Error: {e}")

# === SCHEDULER LOOP ===
def run_bot():
    print("🚀 BOT STARTED")
    send_sms("🚀 BOT RUNNING (Dual Market)...")
    schedule.every(10).minutes.do(trade_stocks)
    schedule.every(15).minutes.do(trade_crypto)
    while True:
        schedule.run_pending()
        time.sleep(1)

run_bot()
