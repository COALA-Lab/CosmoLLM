from . import fit_data
import numpy as np


def calculate_chi(
    data: fit_data.FitresData,
    H: np.ndarray,
    h: float,
    sigma: np.ndarray,
    E_value: np.ndarray
) -> np.ndarray:
    return calculate_chi_hz(H, h, sigma, E_value) + calculate_chi_sn(data)


def calculate_chi_sn(data: fit_data.FitresData):
    C_inv = np.linalg.inv(data.cov_matrix)
    one_vec = np.ones(C_inv.shape[0])
    D = one_vec.T @ C_inv @ one_vec
    B = data.delta_mu.T @ C_inv @ one_vec
    A = data.delta_mu.T @ C_inv @ data.delta_mu

    return A + np.log(D / (2 * np.pi)) - (B**2) / D


def calculate_chi_hz(
    H: np.ndarray,
    h: float,
    sigma: np.ndarray,
    E_value: np.ndarray
) -> np.floating:
    return np.sum(((H - 100 * h * E_value) / sigma) ** 2, axis=0)
