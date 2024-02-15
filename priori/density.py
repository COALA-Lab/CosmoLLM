from .priori_base import priori, PrioriContext, uniform, gaussian



#
@priori('gaussian_around_one')
def gaussian_around_one(context: PrioriContext):
    return gaussian(context.density, 1, 0.1)
