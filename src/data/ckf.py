from irw import KalmanFilter, IRWmodel
import numpy as np
from shared import get_initial_state
from stock_data import get_stock_data
from config import KAPPA, SIGMA_V, NUM_OF_FILTERS


def calculate_weighted_sum(weights: list[float], forecasts_per_model: list[float]
        ) -> float:
    """
        Ŝ_k = sum_{i=1}^{R} mu^i_k * Ŝ^i_k
    """
    weighted_sum = 0.0
    for i in range(len(weights)):
        weighted_sum += weights[i] * forecasts_per_model[i]
    return weighted_sum


def compute_prediction_error_vector(actual_values: list[float], predicted_values: list[float]
        ) -> list[float]:
    """
        returns vector: eps^i_{k+l|k}
        size: (L,)
    """
    actual = np.asarray(actual_values, dtype=float)
    predicted = np.asarray(predicted_values, dtype=float)
    return actual - predicted


def compute_eta(steps: int, actual_values: list[float], predicted_values: list[float]
        ) -> float:
    """
        steps: L
        returns: eta
    """
    prediction_error_vector = compute_prediction_error_vector(actual_values, predicted_values)
    epsilon_powered = prediction_error_vector ** 2
    absolute_sum = abs(np.sum(epsilon_powered))
    eta = float(absolute_sum ** (-steps / 2))
    return eta


def compute_weights(eta_values: list[float]) -> list[float]:
    """
        mu^i_k = eta^i_k / sum_j(eta^j_k)
        returns: vector of weights mu^i_k, size (R,)
    """
    eta = np.asarray(eta_values, dtype=float)
    return (eta / np.sum(eta)).tolist()


def run_ckf(prices: list[float], filter_orders: list[int], sigma_v2: float,
            kappa: float, L: int, verbose: bool = True, print_final: bool = True):
    """
        Pełny flow CKF: trening filtrów r=filter_orders na warmup_prices,
        ocena bledu na window_prices, wagi, polaczona prognoza.

        returns: (weights: dict[int,float], forecasts_on_window: dict[int,list[float]],
                  window_prices: list[float])
    """
    warmup_prices = prices[:-L]
    window_prices = prices[-L:]

    if verbose:
        print(f"warmup_prices (ostatnie 5): {warmup_prices[-5:]}")
        print(f"window_prices (do oceny): {window_prices}")
        print("===")

    forecasts_on_window = {}
    eta_values = {}

    for order in filter_orders:
        model = IRWmodel(order, sigma_v2, kappa)

        x0 = get_initial_state(warmup_prices, order)
        kf = KalmanFilter(model=model, x0=x0)

        for S in warmup_prices:
            kf.predict()
            kf.update(S)
            if verbose:
                print(f"r={order}: S={S:.2f}, x_hat={np.round(kf.x, 3)}")

        forecast_window = [kf.forecast(l) for l in range(1, L + 1)]
        forecasts_on_window[order] = forecast_window

        eta = compute_eta(L, window_prices, forecast_window)
        eta_values[order] = eta

        if verbose:
            print(f"r={order}: prognoza na window: {[round(f,3) for f in forecast_window]}")
            print(f"r={order}: eta = {eta:.6e}")
            print("---")

    weights_list = compute_weights(list(eta_values.values()))
    weights = dict(zip(filter_orders, weights_list))

    if verbose:
        print("\nWagi (mu^i_k):")
        for order, w in weights.items():
            print(f"r={order}: waga = {w:.4f}")

    combined_forecasts = [
        calculate_weighted_sum(
            list(weights.values()),
            [forecasts_on_window[order][l] for order in filter_orders]
        )
        for l in range(L)
    ]

    if print_final:
        print("\n=== Koncowa polaczona prognoza (Ŝ_k) ===")
        for l in range(L):
            print(f"l={l+1}: S_hat = {combined_forecasts[l]:.3f}, prawdziwa wartosc = {window_prices[l]:.3f}")

    return weights, forecasts_on_window, window_prices


def run_kappa_experiment(prices, filter_orders, sigma_v2, L, kappa_values):
    """
        Porownuje polaczona prognoze CKF dla roznych wartosci kappa,
        na tych samych danych.
    """
    for kappa_test in kappa_values:
        print(f"\n=== kappa = {kappa_test} ===")
        weights, forecasts_on_window, window_prices = run_ckf(
            prices, filter_orders=filter_orders,
            sigma_v2=sigma_v2, kappa=kappa_test, L=L, verbose=False, print_final=False
        )
        combined_forecasts = [
            calculate_weighted_sum(
                list(weights.values()),
                [forecasts_on_window[order][l] for order in filter_orders]
            )
            for l in range(L)
        ]
        print(f"wagi: { {k: round(v,3) for k,v in weights.items()} }")
        print(f"prognozy: {[round(f,2) for f in combined_forecasts]}")
        print(f"prawdziwe: {[round(p,2) for p in window_prices]}")

        errors = [abs(f - p) for f, p in zip(combined_forecasts, window_prices)]
        print(f"blad bezwzgledny na kazdym kroku: {[round(e,2) for e in errors]}")
        print(f"sredni blad bezwzgledny: {np.mean(errors):.3f}")


def run_sigma_v2_experiment(prices, filter_orders, kappa, L, sigma_v2_values):
    """
        Porownuje polaczona prognoze CKF dla roznych wartosci sigma_v2,
        przy ustalonym kappa.
    """
    for sigma_test in sigma_v2_values:
        print(f"\n=== sigma_v2 = {sigma_test} (kappa={kappa}) ===")
        weights, forecasts_on_window, window_prices = run_ckf(
            prices, filter_orders=filter_orders,
            sigma_v2=sigma_test, kappa=kappa, L=L, verbose=False, print_final=False
        )
        combined_forecasts = [
            calculate_weighted_sum(
                list(weights.values()),
                [forecasts_on_window[order][l] for order in filter_orders]
            )
            for l in range(L)
        ]
        print(f"wagi: { {k: round(v,3) for k,v in weights.items()} }")
        print(f"prognozy: {[round(f,2) for f in combined_forecasts]}")
        print(f"prawdziwe: {[round(p,2) for p in window_prices]}")

        errors = [abs(f - p) for f, p in zip(combined_forecasts, window_prices)]
        print(f"sredni blad bezwzgledny: {np.mean(errors):.3f}")


def run_grid_experiment(prices, filter_orders, L, sigma_v2_values, kappa_values):
    """
        Siatka 2D: testuje kazda kombinacje sigma_v2 x kappa niezaleznie.
    """
    results = []
    for sigma_test in sigma_v2_values:
        for kappa_test in kappa_values:
            weights, forecasts_on_window, window_prices = run_ckf(
                prices, filter_orders=filter_orders,
                sigma_v2=sigma_test, kappa=kappa_test, L=L, verbose=False, print_final=False
            )
            combined_forecasts = [
                calculate_weighted_sum(
                    list(weights.values()),
                    [forecasts_on_window[order][l] for order in filter_orders]
                )
                for l in range(L)
            ]
            errors = [abs(f - p) for f, p in zip(combined_forecasts, window_prices)]
            mean_error = float(np.mean(errors))
            results.append((sigma_test, kappa_test, mean_error))
            print(f"sigma_v2={sigma_test:>6}, kappa={kappa_test:>6} -> sredni blad = {mean_error:.3f}")

    best = min(results, key=lambda r: r[2])
    print(f"\nNajlepsza kombinacja: sigma_v2={best[0]}, kappa={best[1]}, blad={best[2]:.3f}")
    return results


FILTER_ORDERS = list(range(1, NUM_OF_FILTERS + 1))


def run_for_numbers():
    prices = [1,2,3,4,5,6,7,8,9,10,11,12]
    return run_ckf(prices, filter_orders=FILTER_ORDERS, sigma_v2=SIGMA_V, kappa=KAPPA, L=2)


def run_for_aapl():
    prices = list(get_stock_data("AAPL", period="2y", interval="1d"))
    return run_ckf(prices, filter_orders=FILTER_ORDERS, sigma_v2=SIGMA_V, kappa=KAPPA, L=5)


def run_for_intel():
    prices = list(get_stock_data("INTC", period="2y", interval="1d"))
    return run_ckf(prices, filter_orders=FILTER_ORDERS, sigma_v2=SIGMA_V, kappa=KAPPA, L=5)


def run_aapl_kappa_experiment():
    prices = list(get_stock_data("AAPL", period="2y", interval="1d"))
    run_kappa_experiment(
        prices, filter_orders=FILTER_ORDERS, sigma_v2=SIGMA_V, L=5,
        kappa_values=[0.8, 5, KAPPA, 100]
    )


def run_aapl_sigma_experiment():
    prices = list(get_stock_data("AAPL", period="2y", interval="1d"))
    run_sigma_v2_experiment(
        prices, filter_orders=FILTER_ORDERS, kappa=KAPPA, L=5,
        sigma_v2_values=[0.05, SIGMA_V, 1.0, 5.0, 20.0]
    )


def run_aapl_grid_experiment():
    prices = list(get_stock_data("AAPL", period="2y", interval="1d"))
    run_grid_experiment(
        prices, filter_orders=FILTER_ORDERS, L=5,
        sigma_v2_values=[0.05, SIGMA_V, 1.0, 5.0],
        kappa_values=[0.8, 5, KAPPA, 100]
    )


if __name__ == "__main__":
    run_for_aapl()