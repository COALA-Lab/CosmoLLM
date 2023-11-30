import numpy as np
from .priori_base import PrioriContext, priori, gaussian


@priori("g_gaussian_priori")
def g_gaussian_priori(context: PrioriContext):
    g = context.params[0, :].astype(np.float128)
    return gaussian(g, 0.00015, 0.000075)
