import numpy as np
from .priori_base import priori, PrioriContext, uniform



@priori("a_max_uniform_priori")
def a_max_uniform_priori(context: PrioriContext):
    a_max = params[1, :].astype(np.float128)
    return uniform(a_max, 10**10 - 10**3, float('inf'))