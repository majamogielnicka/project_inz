import numpy as np

from estimation.ckf import run_ckf, combine_forecasts


def run_grid_experiment(prices: list[float], filter_orders: list[int], L: int,
                        sigma_v2_values: list[float], kappa_values: list[float]) -> list[tuple]:
    """
        Sprawdza kazda pare (sigma_v2, kappa) i wypisuje blad prognozy.
        Zeby testowac tylko kappa albo tylko sigma_v2, podaj druga liste z jedna wartoscia.

        przyjmuje: listy wartosci sigma_v2 i kappa do przetestowania, L: liczba dni oceny
        zwraca: lista (sigma_v2, kappa, sredni blad bezwzgledny)
    """
    results = []
    for sigma_v2 in sigma_v2_values:
        for kappa in kappa_values:
            weights, forecasts_on_window, window_prices = run_ckf(
                prices, filter_orders, sigma_v2, kappa, L)
            combined = combine_forecasts(weights, forecasts_on_window, L)
            # np.subtract: roznica element po elemencie; np.abs: wartosc bezwzgledna; np.mean: srednia
            mean_error = float(np.mean(np.abs(np.subtract(combined, window_prices))))
            results.append((sigma_v2, kappa, mean_error))
            print(f"sigma_v2={sigma_v2:>6}, kappa={kappa:>6} -> sredni blad = {mean_error:.3f}")

    best = min(results, key=lambda result: result[2])
    print(f"\nNajlepsza para: sigma_v2={best[0]}, kappa={best[1]}, blad={best[2]:.3f}")
    return results