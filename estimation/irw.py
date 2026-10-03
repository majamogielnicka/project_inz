import numpy as np
from math import comb


class IRWmodel:
    def __init__(self, model_order, process_noise, kappa):

        measurment_noise = get_measurment_noise(kappa, process_noise)

        self.r = model_order
        self.process_noise = process_noise
        self.measurment_noise = get_measurment_noise(kappa, process_noise)
        self.H = build_observation_matrix(model_order)
        self.F = build_state_transition_matrix(model_order)
        self.V = build_process_noise_covariance_matrix(model_order, process_noise)
        self.W = build_measurment_covariance_matrix(measurment_noise)

    def step(self, x):
        """
        Not used currently, left as helper for later
        """
        v = sample_process_noise(self.r, self.process_noise)
        w = np.random.normal(0, self.measurment_noise)
        # x(k+1) = F x(k) + v(k)
        x_next = self.F @ x + v
        # S(k) = H x(k) + w(k)
        S = self.H @ x_next + w

        return x_next, S


class KalmanFilter:

    def __init__(self, model, x0, P0 = None):
        #TODO: make P0 more 'dynamic'?

        self.F = model.F
        self.H = model.H
        self.V = model.V
        self.W = model.W  
        self.measurment_noise = model.measurment_noise #dead code
        self.r = model.r
        self.P0 = np.eye(self.r)
        
        x0 = np.asarray(x0, dtype=float)

        if x0.shape != (self.r,):
            raise ValueError(
                f"x0 has to be the same size as model:  ({self.r},), "
                f"and it is currently: {x0.shape}"
            )

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

        # mu = H P H^T + sigma_w^2
        mu = (
            self.H @ self.P_pred @ self.H.T
            + self.W
        )[0, 0]

        # K = P H^T / mu
        K = (
            self.P_pred @ self.H.T
        ).flatten() / mu

        # x = x_pred + K epsilon
        self.x = (
            self.x_pred
            + K * epsilon
        )

        # P = P_pred - mu K K^T
        self.P = (
            self.P_pred
            - mu * np.outer(K, K)
        )

        return self.x, self.P

    def forecast(self, l_steps):
        F_l = np.linalg.matrix_power(self.F, l_steps)
        x_l = F_l @ self.x
        return float((self.H @ x_l)[0])


def get_measurment_noise(kappa, process_noise):
    """
        kappa = sigmav^2/sigmaw^2
        returns raw measrument noise
    """
    process_noise_squared = process_noise**2
    return np.sqrt(process_noise_squared / kappa)


def build_observation_matrix(model_order):
    """
        H = [1 0 ... 0] 
        returns vector H based on model order

        size: 1 x r
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

        returns F matrix based on model order
        size: r x r
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

        returns V matrix based on model order
        size: r x r
    """
    process_noise_covariance_matrix = np.zeros((model_order, model_order))
    process_noise_covariance_matrix[0, 0] = process_noise ** 2
    return process_noise_covariance_matrix


def build_measurment_covariance_matrix(measurment_noise):
    """
        W = cov[w_k] = [sigma_w^2]
        returns W matrix
        size: 1 x 1
    """
    return np.array([[measurment_noise ** 2]])


def sample_process_noise(model_order, process_noise):
    """
        returns v_k vector based on model order
        size: (model_order,)
    """
    proc_cov_matrix = np.zeros(model_order)
    proc_cov_matrix[0] = np.random.normal(0, process_noise)
    return proc_cov_matrix
