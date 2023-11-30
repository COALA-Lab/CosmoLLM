import abc
import numpy as np


class BaseParametrization(abc.ABC):

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, 'name'):
            raise RuntimeError('A sublcass of BaseParametrization must have a defined "name" class attribute!')
        if not hasattr(cls, 'n_params'):
            raise RuntimeError('A sublcass of BaseParametrization must have a defined "n_params" class attribute!')
        return super().__init_subclass__()

    @abc.abstractclassmethod
    def create(cls, cosmo, max_redshift) -> 'BaseParametrization':
        pass

    @abc.abstractmethod
    def eval(self, z: np.ndarray, params: np.ndarray) -> np.ndarray:
        pass

    def __call__(self, z: np.ndarray, params: np.ndarray) -> np.ndarray:
        return self.eval(z, params)


DYNAMIC_N_PARAMS = -1


def density_parametrization(of_name: str, num_of_params: int):
    def _parametrized_density_decorator(klass):
        class _ParametrizedDensity(klass, BaseParametrization):
            name: str = of_name
            n_params: int = num_of_params

        return _ParametrizedDensity
    return _parametrized_density_decorator
