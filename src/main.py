import numpy as np

from data.stock_data import get_stock_data
from data.irw import IRWmodel, KalmanFilter
from data.config import SIGMA_V, KAPPA


if __name__ == "__main__":

    period = "2y"
    interval = "1d"

    prices = get_stock_data("AAPL", period, interval)

    r = int(input("rząd układu: "))
    print("SIGMA_V: ", SIGMA_V)
    print("KAPPA: ", KAPPA)

    model = IRWmodel(r, SIGMA_V, KAPPA)

    x0 = [float(prices[-1 - i]) for i in range(r)]
    kf = KalmanFilter(model, x0)

    estimates = []
    for price in prices:
        kf.predict()
        x_est, P_est = kf.update(price)
        estimates.append(x_est[0])

    print(f"Aktualna cena: {prices[-1]:.2f}")
    print(f"Ostatnia estymacja: {estimates[-1]:.2f}")

    days = 10
    future = [kf.forecast(l) for l in range(1, days + 1)]

    print("\nPrognoza:")
    for i, price in enumerate(future, 1):
        print(f"Dzień {i}: {price:.2f}")