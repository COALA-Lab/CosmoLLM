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
from utils.util import get_cosmology, read_truth_values, generate_experiment_id, load_model



import warnings
from typing import Optional, List

import matplotlib.pyplot as plt


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


def plot_chains(n_dimensions: int,
                chain,
                mu: Optional[list] = None):
    # mu = [1] * n_dimensions
    plt.figure(figsize=(16, 1.5*n_dimensions))
    for d in range(n_dimensions):
        plt.subplot2grid((n_dimensions, 1), (d, 0))
        plt.plot(chain[:, :, d], alpha=0.5)
        if mu and len(mu) > d:
            plt.axhline(y=mu[d])
    plt.tight_layout()


def plot_corner(chain,
                labels: List[str],
                quantiles: Optional[List[float]] = None):
    if quantiles:
        fig, axes = zeus.cornerplot(chain, labels=labels, quantiles=quantiles)
    else:
        fig, axes = zeus.cornerplot(chain, labels=labels)
    plt.tight_layout()


def plot_density(X_fn, z, x_values):
    # x_med = np.median(x_values, axis=1)
    x_mean = np.mean(x_values, axis=0)
    plt.plot(z, X_fn(z, x_mean), label='density')
    plt.xlabel('Z')
    plt.ylabel('X (density)')
    plt.title('Density')
    # plt.legend()

def plot(experiment_path: str) -> None:
    warnings.filterwarnings("ignore")

    results_path = Path(experiment_path)
    config_path = results_path / 'config.json'
    config = load_model(ExperimentConfig, config_path)

    density_fn_factory = get_parametrization(config.parametrization.name)
    cosmo = get_cosmology(config.cosmo)
    density_fn = density_fn_factory.create(cosmo, config.max_redshift)
    # _, z, _ = read_truth_values(config.max_redshift, config.truth_values)

    z = np.linspace(0, config.max_redshift, 100).reshape(-1, 1)

    ndims = len(config.parametrization.param_names) + 2

    for rank in range(config.nchains):
        chain = np.load(results_path / f'chain_{rank}.npy')

        plot_chains(ndims, chain)
        plt.savefig(results_path / f'chain_{rank}.png')
        plt.clf()

        chain_flat = np.load(results_path / f'chain_{rank}_flat.npy')
        plot_corner(chain_flat, labels=['omega_m',
                                        'h',
                                        *config.parametrization.param_names])
        plt.savefig(results_path / f'corners_{rank}.png')
        plt.clf()

        plot_density(density_fn, z, chain_flat[:, 2:])
        plt.savefig(results_path / f'density_{rank}.png')
        plt.clf()


def execute(config_path: str, results_path: str, experiment_id: str, quiet: bool) -> None:
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
    subprocess.run(f"cp {config_path} {experiment_path}/config.json", shell=True)

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
                                                   ndims))
            start[:, 2:] = np.random.uniform(0.9, 1.1,
                                             size=(nwalkers, nparams))
            sampler.run_mcmc(start,
                             nsteps,
                             callbacks=cb,
                             progress=not quiet)
            if rank == 0 and cb:
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
