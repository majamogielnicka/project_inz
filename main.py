from data.stock_data import get_stock_data
from estimation.ckf import run_ckf
from control.cost_function import plan_from_ckf
from helpers.config import SIGMA_V, KAPPA, NUM_OF_FILTERS


def main():
    ticker = "INTC"
    days = 5
    cash = 5000.0
    number_of_stocks = 10.0

    price_history = list(get_stock_data(ticker, "2y", "1d"))
    filter_orders = list(range(1, NUM_OF_FILTERS + 1))

    model_weights, _, _ = run_ckf(price_history, filter_orders, SIGMA_V, KAPPA, days)

    trading_plan = plan_from_ckf(price_history, cash, number_of_stocks, filter_orders,
                                 SIGMA_V, KAPPA, model_weights, days)
    if trading_plan["status"] != "ok":
        raise SystemExit(trading_plan["status"])

    prices = trading_plan["prices"]
    trades = trading_plan["u_sequence"]
    stocks_before_trade = trading_plan["N_sequence"]
    portfolio_value_after = trading_plan["V_after"]

    forecast_prices = [round(price, 2) for price in prices[1:]]
    print(f"{ticker}: cena {price_history[-1]:.2f}, prognoza: {forecast_prices}")
    print()
    print("dzien   cena   kup/sprzedaj   akcje po   wydatek")

    daily_plan = zip(prices, trades, stocks_before_trade)

    for day, (price, trade, stocks_before) in enumerate(daily_plan):
        stocks_after_trade = stocks_before + trade
        spending = trade * price

        print(
            f"{day:>4} "
            f"{price:>7.2f} "
            f"{trade:>+12.2f} "
            f"{stocks_after_trade:>10.2f} "
            f"{spending:>+13.2f}"
        )

    print()
    print(f"Wartosc portfela po {days} dniach: {portfolio_value_after:.2f}")


if __name__ == "__main__":
    main()