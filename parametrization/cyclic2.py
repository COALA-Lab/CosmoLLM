import numpy as np
from .parametrization_base import density_parametrization, BaseParametrization


# TODO: clean up unused code

@density_parametrization('cyclic', 3)
class Cyclic2:

    @classmethod
    def create(cls, cosmo, max_redshift) -> 'BaseParametrization':
        return Cyclic2()

    def eval(self, z: np.ndarray, params: np.ndarray) -> np.ndarray:
        g = params[0, :]
        a_max_to_mth = params[1, :]
        m = params[2, :]

        z_1_m = np.power(z+1, m)
        # for i in range(len(a_max_to_mth)):
        #     print(f'{a_max[i]}**{m[i]}={a_max_to_mth[i]}')
        return 1 - g * z_1_m - 1.0/(z_1_m * a_max_to_mth) + g + 1.0/a_max_to_mth
