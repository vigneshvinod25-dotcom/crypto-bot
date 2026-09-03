import os
import time
import threading
import ccxt
import pandas as pd
import pandas_ta as ta
from flask import Flask

# Flask Server (Render 24/7 ആക്കി നിർത്താൻ)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7 on Binance Testnet!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Crypto Bot Logic
def start_bot():
    # Binance Spot Testnet Setup
    exchange = ccxt.binance({
        'apiKey': '8vT8K69pO2cppwXacKTx0UYgYCLaxEoBAMdd3ur0e4rb1TVuasN66eJPIaYkDdxL',
        'secret': 'HkDJtlVYlf5sncC1Fi4Y95A3JX8WAcsUI0VBjCEzloP3K0G5NBDlOQFdfguyvh3Q',
        'enableRateLimit': True,
    })
    
    # Binance Spot Testnet URL കാണിക്കുന്നത്
    exchange.set_sandbox_mode(True) 
    
    symbol = 'ETH/USDT'
    timeframe = '5m'
    in_position = False

    while True:
        try:
            # 5-minute Chart Data എടുക്കുന്നു
            bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # EMA Calculation
            df['ema9'] = ta.ema(df['close'], length=9)
            df['ema21'] = ta.ema(df['close'], length=21)

            # Crossover Check
            prev_ema9 = df['ema9'].iloc[-3]
            prev_ema21 = df['ema21'].iloc[-3]
            curr_ema9 = df['ema9'].iloc[-2]
            curr_ema21 = df['ema21'].iloc[-2]

            # Buy Signal (Bullish Crossover)
            if prev_ema9 < prev_ema21 and curr_ema9 > curr_ema21 and not in_position:
                print("BUY Signal Generated for ETH/USDT!")
                # Market Buy Order (ഉദാഹരണത്തിന് 0.05 ETH)
                order = exchange.create_market_buy_order(symbol, 0.05)
                print(order)
                in_position = True

            # Sell Signal (Bearish Crossover)
            elif prev_ema9 > prev_ema21 and curr_ema9 < curr_ema21 and in_position:
                print("SELL Signal Generated for ETH/USDT!")
                # Market Sell Order
                order = exchange.create_market_sell_order(symbol, 0.05)
                print(order)
                in_position = False

        except Exception as e:
            print(f"Error: {e}")

        # ഓരോ 1 മിനിറ്റിലും ചെക്ക് ചെയ്യും
        time.sleep(60)

# 24/7 Threading Setup
if __name__ == "__main__":
    t = threading.Thread(target=start_bot)
    t.start()
    run_flask()
