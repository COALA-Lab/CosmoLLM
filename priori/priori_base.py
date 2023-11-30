import numpy as np


class PrioriContext:
    __slots__ = (
        'hubble',
        'omega_m',
        'density',
        'params'
    )

    def __init__(self,
                 hubble: float,
                 omega_m: float,
                 density: float,
                 params: np.ndarray) -> None:
        self.hubble = hubble
        self.omega_m = omega_m
        self.density = density
        self.params = params

    def __repr__(self) -> str:
        return (
            f'PrioriContext('
            f'hubble={self.hubble}, omega_m={self.omega_m}, density={self.density}, params={self.params}'
            f')'
        )


class PrioriFunction:
    pass


def priori(of_name: str):
    def _decorator(fn):
        class _PrioriFn(PrioriFunction):
            name = of_name

            @classmethod
            def eval(self, context: PrioriContext):
                return fn(context)
        return _PrioriFn
    return _decorator


def gaussian(m, mu, sigma):
    return np.sum(-0.5 * ((m - mu) / sigma) ** 2, axis=0)


def uniform(val, low, high):
    return np.where(np.logical_and(val >= -low, val <= high), 0.0, -np.inf)
