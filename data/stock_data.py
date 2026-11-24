import yfinance as yf
from yfinance.exceptions import YFRateLimitError, YFTickerMissingError

from helpers import messages

# bledy yfinance maja byc rzucane, a nie tylko wypisywane
yf.config.debug.hide_exceptions = False

period = "2y"
interval = "1d"

class StockDataError(Exception):
    """
        Blad pobierania notowan.
    """


def get_stock_data(ticker, period, interval, mode=None):
    """
        Pobiera notowania z Yahoo Finance.

        przyjmuje: ticker: symbol, period/interval: jak w yfinance, mode: Open/High/Low/Close
        zwraca: wektor cen z wybranej kolumny, od najstarszej do najnowszej
        rzuca: StockDataError, gdy yfinance zglosi blad (zly symbol, brak polaczenia, limit zapytan)
    """
    try:
        historical_data = yf.Ticker(ticker).history(period=period, interval=interval)
    except YFTickerMissingError as error:
        raise StockDataError(messages.TICKER_DELISTED.format(ticker=ticker)) from error
    except YFRateLimitError as error:
        raise StockDataError(messages.RATE_LIMIT) from error
    except Exception as error:
        # nieznany symbol
        if getattr(getattr(error, "response", None), "status_code", None) == 404:
            raise StockDataError(messages.TICKER_NOT_FOUND.format(ticker=ticker)) from error
        raise StockDataError(messages.DOWNLOAD_FAILED.format(ticker=ticker, error=error)) from error

    if mode is None:
        mode = get_mode()
    prices = historical_data[mode].dropna().values

    return prices


def get_mode():
    parameter = input("mode: O, C, L, H: ")
    if parameter == "O":
        mode = "Open"
    elif parameter == "H":
        mode = "High"
    elif parameter == "C":
        mode = "Close"
    elif parameter == "L":
        mode = "Low"
    return mode


if __name__=="__main__":
    data = get_stock_data("INTC", period, interval)