import numpy as np
from math import comb

# Wzmocnienie filtru zalezy tylko od kappa, wiec sigma_w mozna unormowac do 1
MEASUREMENT_NOISE = 1.0


class IRWmodel:
    def __init__(self, model_order, kappa):

        process_noise = get_process_noise(kappa)
        measurement_noise = MEASUREMENT_NOISE

        self.r = model_order
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.H = build_observation_matrix(model_order)
        self.F = build_state_transition_matrix(model_order)
        self.V = build_process_noise_covariance_matrix(model_order, process_noise)
        self.W = build_measurement_covariance_matrix(measurement_noise)

    def step(self, x):
        """
            Symuluje jeden krok modelu. Obecnie nieuzywane, zostawione na pozniej.

            przyjmuje: x: obecny stan
            zwraca: nastepny stan x(k+1) i pomiar S(k+1)
        """
        v = sample_process_noise(self.r, self.process_noise)
        w = np.random.normal(0, self.measurement_noise)
        # x(k+1) = F x(k) + v(k)
        x_next = self.F @ x + v
        # S(k) = H x(k) + w(k)
        S = self.H @ x_next + w

        return x_next, S


class KalmanFilter:

    def __init__(self, model, x0, P0 = None):

        self.F = model.F
        self.H = model.H
        self.V = model.V
        self.W = model.W  
        self.measurement_noise = model.measurement_noise  # nieuzywane
        self.r = model.r
        # P_{0|0} = sigma_w^2 * I_R
        self.P0 = model.W[0, 0] * np.eye(self.r) if P0 is None else P0
        
        x0 = np.asarray(x0, dtype=float)

        self.x = x0
        self.P = np.asarray(self.P0, dtype=float)

    def predict(self):

        self.x_pred = self.F @ self.x

        # P(k|k-1) = F P F^T + V
        self.P_pred = (
            self.F @ self.P @ self.F.T
            + self.V
        )

        return self.x_pred, self.P_pred

    def update(self, S):

        # epsilon = S - H x_pred
        epsilon = (
            S - (self.H @ self.x_pred)[0]
        )

        # Q = H P H^T + sigma_w^2
        Q = (
            self.H @ self.P_pred @ self.H.T
            + self.W
        )[0, 0]

        # K = P H^T / Q
        K = (
            self.P_pred @ self.H.T
        ).flatten() / Q

        # x = x_pred + K epsilon
        self.x = (
            self.x_pred
            + K * epsilon
        )

        # P = P_pred - Q K K^T
        self.P = (
            self.P_pred
            - Q * np.outer(K, K)
        )

        return self.x, self.P

    def forecast(self, l_steps):
        F_l = np.linalg.matrix_power(self.F, l_steps)
        x_l = F_l @ self.x
        return float((self.H @ x_l)[0])


def get_process_noise(kappa):
    """
        kappa = sigma_v^2 / sigma_w^2, przy sigma_w = MEASUREMENT_NOISE
        zwraca: sigma_v, odchylenie standardowe szumu procesu
    """
    return MEASUREMENT_NOISE * np.sqrt(kappa)


def build_observation_matrix(model_order):
    """
        H = [1 0 ... 0]
        zwraca: macierz obserwacji H dla danego rzedu modelu, rozmiar (1, r)
    """
    observation_matrix = np.zeros((1, model_order))
    observation_matrix[0][0] = 1.0
    return observation_matrix


def build_state_transition_matrix(model_order):
    """
        F = [-f1 -f2 ..  -fr-1  -fr]
            [1    0   ...  0      0]
            [..   ..  ..   ..    ..]
            [0    0   ..   1      0]

        zwraca: macierz przejscia stanu F dla danego rzedu modelu, rozmiar (r, r)
    """
    f = []

    for i in range(model_order + 1):
        f_i = ((-1) ** i * comb(model_order, i))
        f.append(f_i)

    f = np.array(f)

    state_transition_matrix = np.zeros((model_order, model_order))
    state_transition_matrix[0, :] = -1*(f[1:])
    
    for i in range(1, model_order):
        state_transition_matrix[i, i - 1] = 1.0

    return state_transition_matrix


def build_process_noise_covariance_matrix(model_order, process_noise):
    """
        V = cov[v_k] =
            [sigma_v^2   0_{1x(r-1)}    ]
            [0_{(r-1)x1} 0_{(r-1)x(r-1)}]

        zwraca: macierz kowariancji szumu procesu V dla danego rzedu modelu, rozmiar (r, r)
    """
    process_noise_covariance_matrix = np.zeros((model_order, model_order))
    process_noise_covariance_matrix[0, 0] = process_noise ** 2
    return process_noise_covariance_matrix


def build_measurement_covariance_matrix(measurement_noise):
    """
        W = cov[w_k] = [sigma_w^2]
        zwraca: macierz kowariancji szumu pomiaru W, rozmiar (1, 1)
    """
    return np.array([[measurement_noise ** 2]])


def sample_process_noise(model_order, process_noise):
    """
        Losuje szum procesu v_k (niezerowy tylko pierwszy element).
        zwraca: wektor v_k, rozmiar (r,)
    """
    proc_cov_matrix = np.zeros(model_order)
    proc_cov_matrix[0] = np.random.normal(0, process_noise)
    return proc_cov_matrix
