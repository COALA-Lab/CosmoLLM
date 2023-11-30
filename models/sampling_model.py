import numpy as np
import astropy.cosmology as cosmology


# TODO: clean up unused code

def _omega_r_calc_factory(cosmo: cosmology.FLRW):
    if cosmo.has_massive_nu:
        return lambda z: cosmo.Ogamma0 + cosmo.Ogamma0 * cosmo.nu_relative_density(z)
    else:
        return lambda _: cosmo.Ogamma0 + cosmo.Onu0


class _EFunc:

    def __init__(self, cosmo: cosmology.FLRW):
        self._omega_r_fn = _omega_r_calc_factory(cosmo)
        self._cosmo = cosmo
        self._omega_m = self._cosmo.Om0

    def __call__(self, z: np.ndarray, density_value) -> np.ndarray:
        omega_r = self._omega_r_fn(z)
        z_plus_one = z + 1
        return (z_plus_one ** 3) * self._omega_m + \
               (z_plus_one ** 4) * omega_r + \
               (1 - self._omega_m - omega_r) * density_value

        # return (z_p1**3) * (self._omega_m + z_p1 * omega_r) + (
        #     1 - self._omega_m - omega_r
        # ) * self._density_fn(z, self._x)


def create_E_function(cosmo: cosmology.FLRW):
    # omega_r_fn = _omega_r_calc_factory(cosmo)

    return _EFunc(cosmo)

    # return _E_func
