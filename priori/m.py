import numpy as np
from .priori_base import priori, PrioriContext, gaussian


@priori("m_gaussian_priori")
def m_gaussian_priori(context: PrioriContext):
    # Make the `m` be in the gaussian distribution around 4.25, with 0.3 variance
    # so its ~ [4, 4.5] - do not make the interval strict
    m = context.params[2, :].astype(np.float128)
    return gaussian(m, 4.25, 0.3)
