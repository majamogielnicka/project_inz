import yfinance as yf


period = "2y"
interval = "1d"

def get_stock_data(ticker, period, interval):

    stock = yf.Ticker(ticker)

    historical_data = stock.history(period, interval)

    historical_data = historical_data[
        [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    ]
    mode = get_mode()
    reversed = (historical_data)[mode].values

    return reversed


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
    else:
        raise ValueError ("Unknown parameter")
    return mode


if __name__=="__main__":
    data = get_stock_data("INTC", period, interval)