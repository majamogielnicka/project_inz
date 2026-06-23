import yfinance as yf

symbol = "AAPL"

df = yf.download(symbol, period="10d", interval="1d")
print(df)