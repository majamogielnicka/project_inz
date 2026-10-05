import numpy as np
from scipy.optimize import linprog


def compute_delta_s(prices: list[float]) -> list[float]:
    """
        Delta_S_{k+1} = S_{k+1} - S_k

        przyjmuje: prices: [S_k, ..., S_{k+L}] - L+1 cen
        zwraca:  wektor roznic cen, rozmiar (L,)
    """
    return np.diff(np.asarray(prices, dtype=float)).tolist()


def compute_account_value(money_input: float, number_of_stocks: float, price_of_stock_in_current_moment: float) -> float:
    """
        V_k = M_k + N_k * S_k
        zwraca: wartosc konta
    """
    return money_input + number_of_stocks * price_of_stock_in_current_moment


def compute_expected_profit(trades: list[float], stocks_before_trade: list[float], delta_s: list[float]) -> float:
    """
        FUNKCJA CELU

        sum_l (u_l + N_l) * Delta_S_{l+1}
        trades- ile kupic/sprzedac
        stocks_before_trade - liczba posiadanych akcji
        delta_s: roznice cen z compute_delta_s
        zwraca: zysk lub strata konta po L dniach; V_{k+L} - V_k
    """
    # np.dot: mnozy element po elemencie i sumuje wyniki
    return float(np.dot(np.add(trades, stocks_before_trade), delta_s))


def compute_value_after_horizon(account_value: float, trades: list[float],
                                stocks_before_trade: list[float], delta_s: list[float]) -> float:
    """
        V_{k+L} = V_k + compute_expected_profit

        przyjmuje: account_value: obecna wartosc konta, reszta jak w compute_expected_profit
        zwraca: wartosc konta po L dniach
    """
    return account_value + compute_expected_profit(trades, stocks_before_trade, delta_s)


def build_lp_cost_vector(delta_s: list[float]) -> np.ndarray:
    """
        Wspolczynniki funkcji celu dla linprog. Zmienne: x = [u_0..u_{L-1}, N_0..N_{L-1}].
        linprog minimalizuje

        przyjmuje: delta_s: roznice cen (L)
        zwraca: wektor c, rozmiar (2L)
    """
    delta_s = np.asarray(delta_s, dtype=float)

    return -np.concatenate([delta_s, delta_s])  # np.concatenate: skleja tablice w jedna


def build_lp_problem(account_value: float, current_stocks: float, prices: list[float],
                     spend_lower: float, spend_upper: float) -> dict:
    """
        Sklada macierze LP dla linprog. Zmienne: x = [u_0..u_{L-1}, N_0..N_{L-1}].
        - equality_matrix, equality_values: N_0 = obecna liczba akcji, N_l = N_{l-1} + u_{l-1}
        - inequality_matrix, inequality_limits: konto nie spada ponizej zera w zadnym dniu (V >= 0)
        - variable_limits: wydatek u_l * S_l w przedziale [spend_lower, spend_upper], N bez ograniczen

        przyjmuje:
            account_value: obecna wartosc konta [$]
            current_stocks: obecna liczba akcji
            prices: [S_k, ..., S_{k+L}] - dzisiejsza cena + prognoza
            spend_lower (<0), spend_upper (>0): limit wydatku na jeden dzien [$]
        zwraca: slownik z macierzami cost_vector, equality_matrix, equality_values, inequality_matrix, inequality_limits, variable_limits oraz L
    """
    prices = np.asarray(prices, dtype=float)
    delta_s = np.diff(prices)
    horizon = len(delta_s) # L
    price_at_decision = prices[:-1] # cena w dniu, w ktorym podejmujemy decyzje

    shifted = np.eye(horizon, k=-1)
    equality_matrix = np.hstack([-shifted, np.eye(horizon) - shifted]) #skleja macierze obok siebie
    equality_values = np.zeros(horizon)             
    equality_values[0] = current_stocks

    # np.tril(np.ones): macierz trojkatna dolna 
    negative_profit_matrix = -np.tril(np.ones((horizon, horizon))) * delta_s
    inequality_matrix = np.hstack([negative_profit_matrix, negative_profit_matrix])
    inequality_limits = np.full(horizon, float(account_value))

    variable_limits = [(spend_lower / s, spend_upper / s) for s in price_at_decision]
    variable_limits += [(None, None)] * horizon
    return {"cost_vector": build_lp_cost_vector(delta_s), "equality_matrix": equality_matrix, "equality_values": equality_values,
            "inequality_matrix": inequality_matrix, "inequality_limits": inequality_limits, "variable_limits": variable_limits, "L": horizon}


def solve_mpc_step(account_value: float, current_stocks: float, prices: list[float],
                   spend_lower: float, spend_upper: float) -> dict:
    """
        Rozwiazuje LP z build_lp_problem (te same argumenty).

        zwraca: slownik
            status: "ok" albo komunikat bledu solvera (wtedy brak reszty kluczy)
            u_sequence: ile akcji kupic/sprzedacw kazdym dniu, (L,)
            N_sequence: liczba akcji przed transakcja w kazdym dniu,  (L,)
            objective: przewidywany zysk
            V_after: przewidywana wartosc konta po L dniach
    """
    problem = build_lp_problem(account_value, current_stocks, prices, spend_lower, spend_upper)
    # linprog: solver programowania liniowego, "highs" to jego szybka metoda
    result = linprog(problem["cost_vector"], A_ub=problem["inequality_matrix"], b_ub=problem["inequality_limits"],
                     A_eq=problem["equality_matrix"], b_eq=problem["equality_values"],
                     bounds=problem["variable_limits"], method="highs")
    if not result.success:
        return {"status": result.message}

    horizon = problem["L"]
    trades = result.x[:horizon].tolist()       
    stocks_before_trade = result.x[horizon:].tolist()
    delta_s = compute_delta_s(prices)
    return {"status": "ok", "u_sequence": trades, "N_sequence": stocks_before_trade,
            "objective": compute_expected_profit(trades, stocks_before_trade, delta_s),
            "V_after": compute_value_after_horizon(account_value, trades, stocks_before_trade, delta_s)}


def plan_from_ckf(price_history: list[float], money: float, number_of_stocks: float,
                  filter_orders: list[int], sigma_v2: float, kappa: float,
                  weights: dict, days: int, spend_fraction: float = 0.10) -> dict:
    """
        Liczy prognoze cen na `days` dni i uruchamia
        solve_mpc_step z limitem wydatku +-spend_fraction * wartosc konta na dzien.

        przyjmuje:
            price_history: historia cen, ostatnia = dzisiejsza
            money: gotowka, number_of_stocks: liczba akcji
            weights: wagi modeli z run_ckf
        zwraca: to samo co solve_mpc_step plus klucz
        prices: [dzisiejsza cena, prognoza...], rozmiar (days+1,)
    """
    from estimation.ckf import forecast_future_ckf

    forecast = forecast_future_ckf(price_history, filter_orders=filter_orders,
                                   sigma_v2=sigma_v2, kappa=kappa,
                                   weights=weights, days=days)
    prices = [price_history[-1]] + list(forecast)
    account_value = compute_account_value(money, number_of_stocks, prices[0])
    limit = spend_fraction * account_value
    plan = solve_mpc_step(account_value, number_of_stocks, prices, -limit, limit)
    plan["prices"] = prices
    return plan