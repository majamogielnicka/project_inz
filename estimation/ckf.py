import numpy as np

from estimation.irw import KalmanFilter, IRWmodel
from helpers.shared import get_initial_state


def calculate_weighted_sum(weights: list[float], forecasts_per_model: list[float]) -> float:
    """
        S_hat_{k+l} = sum_r alpha^(r)_k * S_hat^(r)_{k+l}

        przyjmuje:
            weights: wektor wag modeli
            forecasts_per_model: wektor prognoz wszystkich modeli na jeden dzien (po jednej na model)
        zwraca: jedna prognoze ceny (srednia wazona modeli)
    """
    # np.dot: mnozy wagi przez prognozy element po elemencie i sumuje wyniki
    return float(np.dot(weights, forecasts_per_model))


def compute_eta(steps: int, actual_values: list[float], predicted_values: list[float]) -> float:
    """
        eta^(r)_k = (suma kwadratow bledow prognozy) ** (-L/2)
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
        alpha^(r)_k = eta^(r)_k / sum_i(eta^(i)_k)

        przyjmuje: eta_values: wektor eta, po jednej na model
        zwraca: wektor wag modeli (suma wag wynosi 1)
    """
    eta = np.asarray(eta_values, dtype=float)
    return (eta / np.sum(eta)).tolist()


def combine_forecasts(weights: dict[int, float], forecasts_per_model: dict[int, list[float]],
                      steps: int) -> list[float]:
    """
        Laczy prognozy wszystkich modeli w jedna, dzien po dniu.

        przyjmuje: weights: wagi modeli, forecasts_per_model: prognozy kazdego modelu, steps: liczba dni
        zwraca: wektor polaczonej prognozy cen, po jednej cenie na dzien
    """
    orders = list(weights)

    prognosis = [calculate_weighted_sum([weights[order] for order in orders],
                                   [forecasts_per_model[order][day] for order in orders])
            for day in range(steps)]

    return prognosis


def train_filter(order: int, train_prices: list[float], kappa: float) -> tuple[KalmanFilter, list[float]]:
    """
        Tworzy filtr Kalmana danego rzedu i przepuszcza przez niego ceny po kolei.

        przyjmuje: order: rzad modelu, train_prices: ceny do nauki, kappa: parametr modelu
        zwraca: nauczony filtr (gotowy do kf.forecast) i wektor estymat ceny S_hat_{k|k} z kazdego dnia
    """
    model = IRWmodel(order, kappa)
    kf = KalmanFilter(model=model, x0=get_initial_state(train_prices, order))
    estimates = []
    for price in train_prices:
        kf.predict()
        state, _ = kf.update(price)
        estimates.append(float(state[0]))
    return kf, estimates


def run_ckf(prices: list[float], filter_orders: list[int], kappa: float, L: int):
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
        kf, _ = train_filter(order, warmup_prices, kappa)
        forecasts_on_window[order] = [kf.forecast(day) for day in range(1, L + 1)]
        eta_values.append(compute_eta(L, window_prices, forecasts_on_window[order]))

    weights = dict(zip(filter_orders, compute_weights(eta_values)))
    return weights, forecasts_on_window, window_prices


def forecast_future_ckf(prices: list[float], filter_orders: list[int],
                        kappa: float, weights: dict[int, float], days: int) -> list[float]:
    """
        Uczy filtry na calej historii cen
        i prognozuje `days` dni w przyszlosc.

        przyjmuje: weights: wagi z run_ckf, days: ile dni prognozowac
        zwraca: wektor prognozowanych cen na kolejne dni
    """
    forecasts_per_model = {}
    for order in filter_orders:
        kf, _ = train_filter(order, prices, kappa)
        forecasts_per_model[order] = [kf.forecast(day) for day in range(1, days + 1)]
    return combine_forecasts(weights, forecasts_per_model, days)


def estimate_on_window_ckf(prices: list[float], filter_orders: list[int], kappa: float,
                           weights: dict[int, float]) -> list[float]:
    """
        Estymata ceny dzien po dniu na calym oknie: filtry startuja od pierwszego dnia okna,
        a ich estymaty sa laczone wagami z run_ckf.

        przyjmuje: weights: wagi z run_ckf
        zwraca: wektor estymat, po jednej na kazdy dzien z prices
    """
    estimates_per_model = {order: train_filter(order, prices, kappa)[1] for order in filter_orders}
    return combine_forecasts(weights, estimates_per_model, len(prices))
