
from .priori_base import priori, PrioriContext, gaussian


@priori('gaussian_around_one')
def gaussian_around_zero(context: PrioriContext):
    return gaussian(context.params, 1, 0.1)
