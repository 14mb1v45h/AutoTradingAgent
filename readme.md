# Crypto Auto Trading Agent

## Overview

This application is an automated trading agent for cryptocurrencies, specifically focused on Bitcoin (BTC/USDT) on the Binance exchange. It analyzes the market using a simple Moving Average (MA) crossover strategy, generates buy/sell signals, places trades, manages risk, and provides real-time updates. The app includes a graphical user interface (GUI) built with Tkinter for monitoring and control, as well as a RESTful API endpoint powered by Flask for retrieving status information.

### Key Features
- **Market Analysis**: Uses 50-period and 200-period Simple Moving Average (SMA) crossover to generate buy/sell signals.
- **Trade Placement**: Automatically places market buy/sell orders on Binance via the CCXT library based on generated signals.
- **Risk Management**: Limits risk to 1% of account balance per trade with a 2% stop-loss calculation for position sizing.
- **Real-time Updates**: Fetches current BTC/USD price from CoinGecko API every 5 seconds.
- **Signal Generation**: Produces 'Buy', 'Sell', or 'Hold' signals in real-time.
- **GUI**: Displays current price, signal, account balance, and trade history. Includes buttons to start/stop trading.
- **API Endpoint**: Exposes a `/status` endpoint (e.g., http://127.0.0.1:5000/status) to retrieve JSON data on price, signal, balance, and trades.

**Note**: This is a basic example for educational purposes. Trading involves risk, and this app uses real API keys—use with caution on a test account. Real-world trading bots should include more robust error handling, backtesting, and security measures.

## Requirements

- Python 3.6+
- Binance account with API keys (for trading functionality)
- Internet access (for API calls to CoinGecko and Binance)

## Installation

1. Clone or download the repository/script.
2. Install dependencies from `requirements.txt`:

##AUTHOR : BIVASH NAYAK (iambivash.bn@proton.me)
