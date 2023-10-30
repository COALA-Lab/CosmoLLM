import numpy as np
from .parametrization_base import density_parametrization, BaseParametrization


@density_parametrization('quadratic', num_of_params=2)
class Quadratic:

    def __init__(self, max_redshift: float):
        self.max_redshift = max_redshift

    @classmethod
    def create(cls, cosmo, max_redshift) -> 'BaseParametrization':
        return Quadratic(max_redshift)

    def eval(self, z: np.ndarray, x: np.ndarray) -> np.ndarray:
        linear_part = (z * (4 * x[0] - x[1] - 3)) / self.max_redshift
        quadratic_part = (
            (2 * (z ** 2) * (2 * x[0] - x[1] - 1)) / (self.max_redshift ** 2))
        return 1 + linear_part - quadratic_part
