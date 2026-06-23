import requests
import pandas as pd
from io import StringIO
from config import NASDAQ_LISTED_URL, OTHER_LISTED_URL



def load_nasdaq_stocks():
    response = requests.get(NASDAQ_LISTED_URL)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text), sep="|")

    df = df[df["Symbol"].notna()]
    df = df[~df["Symbol"].astype(str).str.contains("File Creation Time", na=False)]

    df = df.rename(columns={
        "Symbol": "symbol",
        "Security Name": "name",
        "ETF": "etf",
        "Test Issue": "test_issue"
    })

    df["exchange"] = "NASDAQ"

    return df[["symbol", "name", "exchange", "etf", "test_issue"]]


def load_other_stocks():
    response = requests.get(OTHER_LISTED_URL)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text), sep="|")

    df = df[df["ACT Symbol"].notna()]
    df = df[~df["ACT Symbol"].astype(str).str.contains("File Creation Time", na=False)]

    df = df.rename(columns={
        "ACT Symbol": "symbol",
        "Security Name": "name",
        "Exchange": "exchange",
        "ETF": "etf",
        "Test Issue": "test_issue"
    })

    return df[["symbol", "name", "exchange", "etf", "test_issue"]]


def get_all_stocks():
    nasdaq = load_nasdaq_stocks()
    other = load_other_stocks()

    stocks = pd.concat([nasdaq, other], ignore_index=True)

    stocks = stocks[stocks["test_issue"] != "Y"]
    stocks = stocks[stocks["etf"] != "Y"]

    stocks = stocks.drop_duplicates(subset=["symbol"])
    stocks = stocks.sort_values("symbol")

    return stocks


if __name__ == "__main__":
    stocks = get_all_stocks()

    for _, row in stocks.iterrows():
        print(f"{row['symbol']} — {row['name']} — {row['exchange']}")

    print(f"\nLiczba spółek: {len(stocks)}")