# Auto Trading Agent Application for Crypto
# =========================================
# This application analyzes the crypto market (using simple MA crossover signals),
# places trades on Binance (example exchange), manages risk, generates signals,
# provides real-time updates, and includes a GUI and API endpoint.
#
# Dependencies:
# - Run `pip install ccxt flask pandas requests` to install required libraries.
# - Tkinter is standard in Python.
#
# Usage:
# - Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your Binance API credentials.
# - Run the script: python auto_trader.py
# - GUI will open for control and monitoring.
# - API endpoint: http://127.0.0.1:5000/status for current status.
#
# Features:
# - Market Analysis: Uses 50-period and 200-period SMA crossover for buy/sell signals.
# - Trade Placement: Buys/Sells on signals using CCXT.
# - Risk Management: Position sizing based on 1% risk per trade, 2% stop loss.
# - Signals: Generated in real-time.
# - Real-time Updates: Polls CoinGecko for BTC/USD price every 5 seconds.
# - GUI: Displays current price, signals, balance, trades; buttons to start/stop trading.
# - API: Endpoint to get current status (price, signal, balance).

import tkinter as tk
from tkinter import ttk
import threading
import time
import requests
import pandas as pd
import ccxt
from flask import Flask, jsonify
import queue

# Configuration
EXCHANGE = 'binance'
SYMBOL = 'BTC/USDT'
API_KEY = 'YOUR_API_KEY'  # Replace with your Binance API key
API_SECRET = 'YOUR_API_SECRET'  # Replace with your Binance API secret
RISK_PER_TRADE = 0.01  # 1% risk per trade
STOP_LOSS_PCT = 0.02  # 2% stop loss
MA_SHORT = 50
MA_LONG = 200
POLL_INTERVAL = 5  # Seconds for price polling

# Global variables
app = Flask(__name__)
exchange = None
trading_active = False
current_price = 0.0
current_signal = 'Hold'
account_balance = 0.0
trades = []
data_queue = queue.Queue()  # For GUI updates
price_history = []  # List to store price data for analysis

def init_exchange():
    global exchange
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
    })
    # Fetch initial balance (USDT)
    global account_balance
    balance = exchange.fetch_balance()
    account_balance = balance['USDT']['free']

def fetch_price():
    """Fetch real-time price from CoinGecko (free API)."""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return 0.0

def analyze_market():
    """Analyze market using SMA crossover."""
    if len(price_history) < MA_LONG:
        return 'Hold'
    
    df = pd.DataFrame(price_history, columns=['price'])
    df['sma_short'] = df['price'].rolling(window=MA_SHORT).mean()
    df['sma_long'] = df['price'].rolling(window=MA_LONG).mean()
    
    if df['sma_short'].iloc[-1] > df['sma_long'].iloc[-1] and df['sma_short'].iloc[-2] <= df['sma_long'].iloc[-2]:
        return 'Buy'
    elif df['sma_short'].iloc[-1] < df['sma_long'].iloc[-1] and df['sma_short'].iloc[-2] >= df['sma_long'].iloc[-2]:
        return 'Sell'
    return 'Hold'

def place_trade(signal):
    """Place trade with risk management."""
    global account_balance
    if signal == 'Buy':
        # Calculate position size
        stop_price = current_price * (1 - STOP_LOSS_PCT)
        risk_amount = account_balance * RISK_PER_TRADE
        position_size = risk_amount / (current_price - stop_price)  # In BTC
        
        try:
            order = exchange.create_market_buy_order(SYMBOL, position_size)
            trades.append(f"Bought {position_size} BTC at {current_price}")
            # Update balance (simplified, real would fetch again)
            account_balance -= position_size * current_price
        except Exception as e:
            trades.append(f"Buy error: {e}")
    elif signal == 'Sell':
        # Assume we sell all for simplicity; in real, track positions
        balance_btc = exchange.fetch_balance()['BTC']['free']
        if balance_btc > 0:
            try:
                order = exchange.create_market_sell_order(SYMBOL, balance_btc)
                trades.append(f"Sold {balance_btc} BTC at {current_price}")
                account_balance += balance_btc * current_price
            except Exception as e:
                trades.append(f"Sell error: {e}")

def trading_loop():
    global current_price, current_signal, trading_active
    while trading_active:
        price = fetch_price()
        if price > 0:
            current_price = price
            price_history.append(price)
            if len(price_history) > MA_LONG * 2:  # Keep recent data
                price_history.pop(0)
            signal = analyze_market()
            current_signal = signal
            data_queue.put(('update', current_price, current_signal))
            
            if signal in ['Buy', 'Sell']:
                place_trade(signal)
                data_queue.put(('trade', trades[-1] if trades else ''))
        
        time.sleep(POLL_INTERVAL)

# Flask API
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'price': current_price,
        'signal': current_signal,
        'balance': account_balance,
        'trades': trades
    })

def run_flask():
    app.run(debug=False, use_reloader=False)

# GUI
class TradingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Auto Trader")
        
        self.price_label = ttk.Label(root, text="Current Price: $0.00")
        self.price_label.pack(pady=10)
        
        self.signal_label = ttk.Label(root, text="Signal: Hold")
        self.signal_label.pack(pady=10)
        
        self.balance_label = ttk.Label(root, text="Balance: $0.00")
        self.balance_label.pack(pady=10)
        
        self.trades_list = tk.Listbox(root, height=10, width=50)
        self.trades_list.pack(pady=10)
        
        self.start_button = ttk.Button(root, text="Start Trading", command=self.start_trading)
        self.start_button.pack(side=tk.LEFT, padx=20)
        
        self.stop_button = ttk.Button(root, text="Stop Trading", command=self.stop_trading)
        self.stop_button.pack(side=tk.RIGHT, padx=20)
        
        self.update_gui()

    def start_trading(self):
        global trading_active
        if not trading_active:
            trading_active = True
            threading.Thread(target=trading_loop, daemon=True).start()

    def stop_trading(self):
        global trading_active
        trading_active = False

    def update_gui(self):
        try:
            while not data_queue.empty():
                msg = data_queue.get_nowait()
                if msg[0] == 'update':
                    self.price_label.config(text=f"Current Price: ${msg[1]:.2f}")
                    self.signal_label.config(text=f"Signal: {msg[2]}")
                    self.balance_label.config(text=f"Balance: ${account_balance:.2f}")
                elif msg[0] == 'trade':
                    self.trades_list.insert(tk.END, msg[1])
        except queue.Empty:
            pass
        self.root.after(1000, self.update_gui)

if __name__ == "__main__":
    init_exchange()
    
    # Start Flask in a thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start GUI
    root = tk.Tk()
    gui = TradingGUI(root)
    root.mainloop()