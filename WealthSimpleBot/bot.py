import os
import logging
import pandas as pd
from dotenv import load_dotenv
from wealthsimple import Wealthsimple
import yfinance as yf
import time

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "Personal Account")
SECURITY = os.getenv("SECURITY", "AAPL")
TRADE_AMOUNT = float(os.getenv("TRADE_AMOUNT", 100))
SHORT_WINDOW = int(os.getenv("SHORT_WINDOW", 10))
LONG_WINDOW = int(os.getenv("LONG_WINDOW", 30))
RSI_OVERBOUGHT = int(os.getenv("RSI_OVERBOUGHT", 70))
RSI_OVERSOLD = int(os.getenv("RSI_OVERSOLD", 30))

# --- SETUP LOGGING ---
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- GLOBAL VARIABLES ---
current_position = None  # Tracks the current position ('long', None)

# --- FUNCTIONS ---

def calculate_trade_size(available_balance, default_size):
    risk_factor = 0.05  # Risk 5% of available balance
    return min(default_size, available_balance * risk_factor)

def get_account_balance(ws, account_id):
    try:
        balance = ws.get_balance(account_id)
        if balance:
            return balance["available"]
        else:
            logging.warning(f"Failed to fetch balance for account ID {account_id}.")
            return 0
    except Exception as e:
        logging.error(f"Error retrieving account balance: {e}")
        return 0

def get_position_size(ws, account_id, ticker):
    try:
        positions = ws.get_positions(account_id)
        for position in positions:
            if position["symbol"] == ticker:
                return position["quantity"]
        logging.warning(f"No position found for ticker {ticker}.")
        return 0
    except Exception as e:
        logging.error(f"Error retrieving position size: {e}")
        return 0

def calculate_vwap(data):
    if "VWAP" not in data.columns:
        data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()
    return data

def place_order(ws, account_id, ticker, size, order_type):
    try:
        ws.place_order(
            account_id=account_id,
            symbol=ticker,
            amount=size,
            order_type=order_type
        )
        logging.info(f"Placed {order_type} order for {ticker} of size {size}.")
    except Exception as e:
        logging.error(f"Error placing {order_type} order for {ticker}: {e}")

def trade_logic(data, ws, account_id, ticker):
    global current_position

    if data is None or data.empty or "price" not in data.columns:
        logging.warning("Data is invalid or missing required fields.")
        return

    latest = data.iloc[-1]
    try:
        price = latest["price"]
        sma_short = latest["SMA_Short"]
        sma_long = latest["SMA_Long"]
        rsi = latest["RSI"]
        vwap = latest.get("VWAP", price)
    except KeyError as e:
        logging.error(f"Missing required indicator {e}. Cannot proceed with trade logic.")
        return

    logging.info(
        f"Indicators - Price: {price:.2f}, SMA Short: {sma_short:.2f}, SMA Long: {sma_long:.2f}, "
        f"VWAP: {vwap:.2f}, RSI: {rsi:.2f}"
    )

    if (price > vwap and sma_short > sma_long and rsi < RSI_OVERSOLD and
            (not current_position or current_position != 'long')):
        logging.info("Advanced Buy Signal triggered.")
        available_balance = get_account_balance(ws, account_id)
        trade_size = calculate_trade_size(available_balance, TRADE_AMOUNT)
        place_order(ws, account_id, ticker, trade_size, "buy")
        current_position = "long"

    elif ((price < vwap or sma_short < sma_long or rsi > RSI_OVERBOUGHT) and
          current_position == "long"):
        logging.info("Advanced Sell Signal triggered.")
        position_size = get_position_size(ws, account_id, ticker)
        place_order(ws, account_id, ticker, position_size, "sell")
        current_position = None

def fetch_stock_data(ticker, period="1d", interval="1m"):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            logging.warning(f"No data fetched for {ticker}.")
            return None
        data["price"] = data["Close"]
        return calculate_vwap(data)
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker}: {e}")
        return None

def initialize_wealthsimple():
    try:
        ws = Wealthsimple(USERNAME, PASSWORD, two_factor_callback=lambda: pyotp.TOTP(AUTH_SECRET_KEY).now())
        logging.info("Logged in to Wealthsimple successfully.")
        return ws
    except Exception as e:
        logging.error(f"Error logging into Wealthsimple: {e}")
        return None

def main():
    ws = initialize_wealthsimple()
    if not ws:
        logging.critical("Wealthsimple session initialization failed. Exiting.")
        return

    account_id = ws.get_account_id(ACCOUNT_NAME)
    if not account_id:
        logging.critical(f"Failed to retrieve account ID for '{ACCOUNT_NAME}'. Exiting.")
        return

    while True:
        try:
            stock_data = fetch_stock_data(SECURITY, period="1d", interval="1m")
            if stock_data is not None:
                trade_logic(stock_data, ws, account_id, SECURITY)
            else:
                logging.warning("No stock data available.")
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
