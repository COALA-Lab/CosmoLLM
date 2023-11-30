from typing import Callable

import numpy as np

HubbleDensityFunc_T = Callable[[np.ndarray], np.ndarray]


def normalized_hubble_squared(
    omega_m: float, omega_r: float, z: np.ndarray, hubble_func: HubbleDensityFunc_T
) -> np.ndarray:
    """
    Calculate E(z)^2 (Squared normalized hubble function H(z)/H(0)) approximated with the
    Hubble density function X(z) (hubble_func parameter)
    """
    return (
        omega_m * (1 + z) ** 3
        + omega_r * (1 + z) ** 4
        + (1 - omega_m - omega_r) * hubble_func(z)
    )


def normalized_hubble(
    omega_m: float, omega_r: float, z: np.ndarray, hubble_func: HubbleDensityFunc_T
) -> np.ndarray:
    """
    Calculate E(z) (Normalized hubble function H(z)/H(0)) approximated with the
    Hubble density function X(z) (hubble_func parameter)
    """
    return np.sqrt(normalized_hubble_squared(omega_m, omega_r, z, hubble_func))


def log_normalized_hubble(
    omega_m: float, omega_r: float, z: np.ndarray, hubble_func: HubbleDensityFunc_T
) -> np.ndarray:
    return 0.5 * np.log(normalized_hubble_squared(omega_m, omega_r, z, hubble_func))


NormalizedHubble_T = Callable[[np.ndarray], np.ndarray]


def create_hubbler(
    omega_m: float,
    omega_r: float,
    hubble_func: HubbleDensityFunc_T,
    squared: bool = False,
) -> NormalizedHubble_T:
    if squared:
        return lambda z: normalized_hubble_squared(omega_m, omega_r, z, hubble_func)
    else:
        return lambda z: normalized_hubble(omega_m, omega_r, z, hubble_func)
