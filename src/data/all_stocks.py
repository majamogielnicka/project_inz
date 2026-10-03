import pandas as pd
import requests
from io import StringIO


def get_assets():

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    html = requests.get(url, headers=headers).text


    sp500 = pd.read_html(
        StringIO(html)
    )[0][
        ["Symbol", "Security"]
    ]


    nasdaq = pd.read_csv(
        "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
        sep="|"
    )


    nyse = pd.read_csv(
        "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
        sep="|"
    )
    assets = {}
    for _, row in sp500.iterrows():
        assets[row["Symbol"]] = row["Security"]

    for _, row in nasdaq.iterrows():
        symbol = row["Symbol"]

        if pd.notna(symbol):
            assets[str(symbol)] = row["Security Name"]


    for _, row in nyse.iterrows():

        symbol = row["ACT Symbol"]

        if pd.notna(symbol):
            assets[str(symbol)] = row["Security Name"]


    assets = { 
        symbol : name
        for symbol, name in assets.items()
        if "$" not in symbol
    }

    return assets


if __name__=="__main__":
    assets = get_assets()
    for symbol in sorted(assets):
        print(symbol)