#!/usr/bin/env python3
import subprocess
from pathlib import Path
from argparse import ArgumentParser
import traceback

import numpy as np
import zeus

from models.experiment_config import ExperimentConfig
from parametrization import get_parametrization
from priori import get_priori, PrioriContext
from utils.fit_data import parse_fits
from utils import chi
from models.sampling_model import create_E_function
from utils.util import get_cosmology, read_truth_values, generate_experiment_id


def log_priori(ctx: PrioriContext):
    return sum(map(lambda prior: prior.eval(ctx), prioris))


def log_posterior(params):
    omega_m = params[:, 0].reshape(1, -1)
    h = params[:, 1].reshape(1, -1)
    x = params[:, 2:].T
    z_matrix = np.transpose([z] * params.shape[0])

    density = density_fn(z_matrix, x)  # X(z) - the parametrized function
    context = PrioriContext(
        h, omega_m, density, x
    )  # Context for evaluating prioris
    log_priori_value = log_priori(context)
    E_value = E_fn(z_matrix, density)
    chi_hz = chi.calculate_chi_hz(H, h, sigma, E_value)
    return log_priori_value - 0.5 * (
            chi_hz + chi_sn
    )


if __name__ == "__main__":
    #############################
    ##### ARGUMENT PARSING ######
    #############################

    parser = ArgumentParser()
    parser.add_argument('config_path', help='Path to experiments configuration file')
    parser.add_argument(
        '--results-path',
        help='Path to the results directory, where the chains will be saved',
        default='/tmp/cosmo_llm_results/'
    )
    parser.add_argument('--experiment-id', help='ID of the experiment', default=None)
    parser.add_argument(
        '-q', '--quiet',
        help='Turn off the progress bar.', action='store_true', default=False
    )

    args = parser.parse_args()
    config = ExperimentConfig.parse_file(args.config_path)

    #############################
    ###### EXPERIMENT INIT ######
    #############################

    density_fn_factory = get_parametrization(config.parametrization.name)
    prioris = [
        get_priori(registry, priori) for registry, priori in config.priori.items()
    ]

    experiment_id = args.experiment_id if args.experiment_id else generate_experiment_id()
    results_path = Path(args.results_path)
    experiment_path = results_path / experiment_id
    subprocess.run(f"mkdir -p {experiment_path}", shell=True)
    subprocess.run(f"cp {args.config_path} {experiment_path}/config.json", shell=True)

    max_redshift = config.max_redshift
    nwalkers = config.nwalkers
    nsteps = config.nsteps
    cosmo = get_cosmology(config.cosmo)
    fits = parse_fits(config.fits_path.fitres,
                      config.fits_path.sys,
                      cosmology=cosmo)
    chi_sn = chi.calculate_chi_sn(data=fits)
    H, z, sigma = read_truth_values(max_redshift, config.truth_values)

    # Make matrices so you can vectorize across all walkers
    H = H.reshape(-1, 1)
    sigma = sigma.reshape(-1, 1)

    E_fn = create_E_function(cosmo)
    density_fn = density_fn_factory.create(cosmo, max_redshift)
    nparams = density_fn.n_params
    ndims = 2 + nparams  # Add h and omega_m params

    ###############################
    ####### EXPERIMENT RUN ########
    ###############################

    with zeus.ChainManager(config.nchains) as chain_manager:
        rank = chain_manager.rank
        chain_path = experiment_path / f'chain_{rank}.npy'
        chain_path_flat = experiment_path / f'chain_{rank}_flat.npy'
        try:
            cb = zeus.callbacks.ParallelSplitRCallback(epsilon=0.01,
                                                       chainmanager=chain_manager)
            sampler = zeus.EnsembleSampler(
                nwalkers, ndims,
                logprob_fn=log_posterior,
                pool=chain_manager.get_pool,
                vectorize=True)

            start = 0.01 * np.random.uniform(0.0, 0.2,
                                             size=(nwalkers,
                                                   ndims)).astype(np.float128)
            start[:, 2:] = np.random.uniform(0.9, 1.1,
                                             size=(nwalkers, nparams)).astype(np.float128)
            sampler.run_mcmc(start,
                             nsteps,
                             callbacks=cb,
                             progress=not args.quiet)
            if rank == 0 and cb:
                print(f'R = {cb.estimates}')
            np.save(chain_path, sampler.get_chain())
            np.save(chain_path_flat, sampler.get_chain(flat=True, discard=0.5))
        except Exception as e:
            print(f"Exception during experiment: {e}")
            traceback.print_exception()
