from .priori_base import priori, PrioriContext, gaussian

#
@priori('gauss')
def gauss_matter_priori(context: PrioriContext):
    return gaussian(context.omega_m, 0.315, 0.021)
