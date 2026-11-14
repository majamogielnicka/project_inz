def get_initial_state(prices: list[float], order: int) -> list[float]:
    """
        Stan poczatkowy filtru: pierwsza cena okna powtorzona `order` razy (brak trendu na starcie).
        Bierze tylko dane z poczatku okna, zeby filtr nie widzial przyszlych cen.
    """
    return [prices[0]] * order
