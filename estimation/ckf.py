import numpy as np

from estimation.irw import KalmanFilter, IRWmodel
from helpers.shared import get_initial_state


def calculate_weighted_sum(weights: list[float], forecasts_per_model: list[float]) -> float:
    """
        S_hat_k = sum_i mu^i_k * S_hat^i_k

        przyjmuje:
            weights: wektor wag modeli
            forecasts_per_model: wektor prognoz wszystkich modeli na jeden dzien (po jednej na model)
        zwraca: jedna prognoze ceny (srednia wazona modeli)
    """
    # np.dot: mnozy wagi przez prognozy element po elemencie i sumuje wyniki
    return float(np.dot(weights, forecasts_per_model))


def compute_eta(steps: int, actual_values: list[float], predicted_values: list[float]) -> float:
    """
        eta^i_k = (suma kwadratow bledow prognozy) ** (-L/2)
        mniejszy blad daje wieksze eta, czyli wieksza waga modelu

        przyjmuje:
            steps: L, liczba dni oceny
            actual_values: wektor faktycznych cen z dni oceny
            predicted_values: wektor prognoz modelu na te same dni
        zwraca: eta modelu
    """
    # np.asarray: lista -> tablica numpy; np.sum: suma elementow
    errors = np.asarray(actual_values, dtype=float) - np.asarray(predicted_values, dtype=float)
    return float(np.sum(errors ** 2) ** (-steps / 2))


def compute_weights(eta_values: list[float]) -> list[float]:
    """
        mu^i_k = eta^i_k / sum_j(eta^j_k)

        przyjmuje: eta_values: wektor eta, po jednej na model
        zwraca: wektor wag modeli (suma wag wynosi 1)
    """
    eta = np.asarray(eta_values, dtype=float)
    return (eta / np.sum(eta)).tolist()


def combine_forecasts(weights: dict[int, float], forecasts_per_model: dict[int, list[float]],
                      steps: int) -> list[float]:
    """
        Laczy prognozy wszystkich modeli w jedna, dzien po dniu.
        zwraca: wektor polaczonej prognozy cen, po jednej cenie na dzien
    """
    orders = list(weights)

    prognosis = [calculate_weighted_sum([weights[order] for order in orders],
                                   [forecasts_per_model[order][day] for order in orders])
            for day in range(steps)]

    return prognosis


def train_filter(order: int, train_prices: list[float], sigma_v2: float, kappa: float) -> KalmanFilter:
    """
        Tworzy filtr Kalmana danego rzedu i przepuszcza przez niego ceny po kolei.

        przyjmuje: order: rzad modelu, train_prices: ceny do nauki, sigma_v2 i kappa: parametry modelu
        zwraca: nauczony filtr (gotowy do kf.forecast)
    """
    model = IRWmodel(order, sigma_v2, kappa)
    kf = KalmanFilter(model=model, x0=get_initial_state(train_prices, order))
    for price in train_prices:
        kf.predict()
        kf.update(price)
    return kf


def run_ckf(prices: list[float], filter_orders: list[int], sigma_v2: float,
            kappa: float, L: int):
    """
        Ocenia modele: uczy filtry na cenach bez ostatnich L dni, prognozuje te L dni
        i na podstawie bledow nadaje modelom wagi.

        przyjmuje: prices: wektor calej historii cen, filter_orders: lista rzedow modeli, L: liczba dni oceny
        zwraca: weights (slownik: rzad modelu, waga),
            forecasts_on_window (slownik: rzad modelu, wektor prognoz na dni oceny),
            window_prices (wektor faktycznych cen z dni oceny)
    """
    warmup_prices = prices[:-L]
    window_prices = prices[-L:]

    forecasts_on_window = {}
    eta_values = []
    for order in filter_orders:
        kf = train_filter(order, warmup_prices, sigma_v2, kappa)
        forecasts_on_window[order] = [kf.forecast(day) for day in range(1, L + 1)]
        eta_values.append(compute_eta(L, window_prices, forecasts_on_window[order]))

    weights = dict(zip(filter_orders, compute_weights(eta_values)))
    return weights, forecasts_on_window, window_prices


def forecast_future_ckf(prices: list[float], filter_orders: list[int], sigma_v2: float,
                        kappa: float, weights: dict[int, float], days: int) -> list[float]:
    """
        prognoza: uczy filtry na calej historii 
        i prognozuje `days` dni w przyszlosc.

        przyjmuje: weights: wagi z run_ckf, days: ile dni prognozowac
        zwraca: wektor prognozowanych cen na kolejne dni
    """
    forecasts_per_model = {}
    for order in filter_orders:
        kf = train_filter(order, prices, sigma_v2, kappa)
        forecasts_per_model[order] = [kf.forecast(day) for day in range(1, days + 1)]
    return combine_forecasts(weights, forecasts_per_model, days)