from .priori_base import priori, gaussian, PrioriContext


@priori('planck')
def planck_h_prior(context: PrioriContext):
    return gaussian(context.hubble, 67.5 / 100., 1.5 / 100.)


@priori('shoes')
def shoes_h_prior(context: PrioriContext):
    return gaussian(context.hubble, 73.5 / 100., 1.5 / 100.)
