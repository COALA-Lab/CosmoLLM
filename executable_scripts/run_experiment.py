#!/usr/bin/env python3

import subprocess
import time
from pathlib import Path
from argparse import ArgumentParser
import traceback
from typing import Optional

import numpy as np
import zeus

from models.experiment_config import ExperimentConfig
from parametrization import get_parametrization
from priori import get_priori, PrioriContext
from utils.fit_data import parse_fits
from utils import chi
from models.sampling_model import create_E_function
from utils.util import get_cosmology, read_truth_values, generate_experiment_id, load_model


density_fn = None
E_fn = None
H = None
sigma = None
chi_sn = None
z = None
prioris = None


def log_priori(ctx: PrioriContext):
    global prioris

    return sum(map(lambda prior: prior.eval(ctx), prioris))


def log_posterior(params):
    global density_fn
    global E_fn
    global H
    global sigma
    global chi_sn
    global z

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


def execute(config_path: str, results_path: str, experiment_id: Optional[str] = None, quiet: bool = False) -> None:
    global density_fn
    global E_fn
    global H
    global sigma
    global chi_sn
    global z
    global prioris

    # Initialize the parametrization and prioris
    config = load_model(ExperimentConfig, config_path)
    density_fn_factory = get_parametrization(config.parametrization.name)
    prioris = [
        get_priori(registry, priori) for registry, priori in config.priori.items()
    ]

    experiment_id = experiment_id if experiment_id else generate_experiment_id()
    results_path = Path(results_path)
    experiment_path = results_path / experiment_id
    subprocess.run(f"mkdir -p {experiment_path}", shell=True)
    subprocess.run(f"cp -n {config_path} {experiment_path}/config.json", shell=True)

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

    # Run the experiment
    with zeus.ChainManager(config.nchains) as chain_manager:
        start_timestamp = time.time()

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
                vectorize=True,
                verbose=not quiet)

            start = 0.01 * np.random.uniform(0.0, 0.2,
                                             size=(nwalkers,
                                                   ndims))
            start[:, 2:] = np.random.uniform(0.9, 1.1,
                                             size=(nwalkers, nparams))
            sampler.run_mcmc(start,
                             nsteps,
                             callbacks=cb,
                             progress=not quiet)

            end_timestamp = time.time()
            if not quiet:
                print(f"Chain {rank} took {end_timestamp - start_timestamp} seconds")

            if rank == 0 and cb and not quiet:
                print(f'R = {cb.estimates}')
            np.save(chain_path, sampler.get_chain())
            np.save(chain_path_flat, sampler.get_chain(flat=True, discard=0.5))
        except Exception as e:
            print(f"Exception during experiment: {e}")
            traceback.print_exception()


if __name__ == "__main__":
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

    # Execute experiment
    execute(args.config_path, args.results_path, args.experiment_id, args.quiet)
