import numpy as np
from .parametrization_base import density_parametrization, BaseParametrization


@density_parametrization('cubic', num_of_params=3)
class Cubic:

    def __init__(self, max_redshift: float):
        self.max_redshift = max_redshift

    @classmethod
    def create(cls, cosmo, max_redshift) -> 'BaseParametrization':
        return Cubic(max_redshift)

    def eval(self, z: np.ndarray, x: np.ndarray) -> np.ndarray:
        z_div = z / (2 * self.max_redshift)
        linear_part = z_div * (-11 + 18 * x[0] - 9 * x[1] + 2 * x[2])

        z_div *= z / self.max_redshift
        quadratic_part = -9 * z_div * (-2 + 5 * x[0] - 4 * x[1] + x[2])

        z_div *= z / self.max_redshift
        cubic_part = 9 * z_div * (-1 + 3 * x[0] - 3 * x[1] + x[2])

        return 1 + cubic_part + quadratic_part + linear_part
