import numpy as np

from estimation.ckf import run_ckf, combine_forecasts


def run_kappa_experiment(prices: list[float], filter_orders: list[int], L: int,
                         kappa_values: list[float]) -> list[tuple]:
    """
        Sprawdza kazda wartosc kappa i wypisuje blad prognozy.

        przyjmuje: kappa_values: lista wartosci kappa do przetestowania, L: liczba dni oceny
        zwraca: lista (kappa, sredni blad bezwzgledny)
    """
    results = []
    for kappa in kappa_values:
        weights, forecasts_on_window, window_prices = run_ckf(prices, filter_orders, kappa, L)
        combined = combine_forecasts(weights, forecasts_on_window, L)
        # np.subtract: roznica element po elemencie; np.abs: wartosc bezwzgledna; np.mean: srednia
        mean_error = float(np.mean(np.abs(np.subtract(combined, window_prices))))
        results.append((kappa, mean_error))
        print(f"kappa={kappa:>6} -> sredni blad = {mean_error:.3f}")

    best = min(results, key=lambda result: result[1])
    print(f"\nNajlepsza kappa: {best[0]}, blad={best[1]:.3f}")
    return results