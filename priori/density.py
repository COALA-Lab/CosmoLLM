from .priori_base import priori, PrioriContext, uniform, gaussian


@priori('uniform_around_zero')
def uniform_around_zero(context: PrioriContext):
    return uniform(context.density, -0.2, 0.2)


@priori('gaussian_around_zero')
def gaussian_around_zero(context: PrioriContext):
    return gaussian(context.density, 0, 0.1)


@priori('gaussian_around_one')
def gaussian_around_one(context: PrioriContext):
    return gaussian(context.density, 1, 0.2)
