# Python Trading Bot with Wealthsimple API

## Overview
This Python-based trading bot integrates with Wealthsimple to perform automated intraday trades based on predefined technical indicators such as SMA, RSI, and VWAP.

### Key Features
- **Technical Analysis**: Utilizes Simple Moving Averages (SMA), Relative Strength Index (RSI), and Volume Weighted Average Price (VWAP).
- **Dynamic Risk Management**: Adjusts trade size based on available account balance and risk parameters.
- **Advanced Logic**: Implements momentum-based strategies using VWAP and RSI thresholds.
- **Wealthsimple Integration**: Fully integrated for account balance, position management, and order execution.
- **Robust Logging**: Logs all operations and signals for debugging and performance tracking.

---

## Configuration
Environment variables are used for sensitive data:
- `USERNAME`: Wealthsimple username.
- `PASSWORD`: Wealthsimple password.
- `AUTH_SECRET_KEY`: 2FA secret key for Wealthsimple.
- `ACCOUNT_NAME`: Name of the Wealthsimple account.
- `SECURITY`: Stock ticker to trade (e.g., `AAPL`).
- `TRADE_AMOUNT`: Default trade amount.
- `SHORT_WINDOW`: Short SMA window size.
- `LONG_WINDOW`: Long SMA window size.
- `RSI_OVERBOUGHT`: RSI threshold for overbought conditions.
- `RSI_OVERSOLD`: RSI threshold for oversold conditions.

---

## Installation
1. Clone the repository.
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file with your configuration.

---

## Usage
Run the script:
```bash
python trading_bot.py
