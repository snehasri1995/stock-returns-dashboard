import yfinance as yf
import pandas as pd
import numpy as np

TICKERS = ["SPY","QQQ","GLD","BND","AAPL","JPM","BLK","XOM","AMZN","MSFT"]

print("Downloading data...")
data = yf.download(TICKERS, start="2022-01-01", end="2024-12-31", auto_adjust=True, progress=False)

prices = data["Close"]
prices.columns = prices.columns.get_level_values(0)
returns = prices.pct_change().dropna()

prices.to_csv("prices.csv")
returns.to_csv("returns.csv")

print(f"Downloaded {len(prices)} days of data")
print("\n--- Annualized Return (%) ---")
print((returns.mean() * 252 * 100).round(2))
print("\n--- Annualized Volatility (%) ---")
print((returns.std() * np.sqrt(252) * 100).round(2))
print("\nDone! prices.csv and returns.csv saved.")
