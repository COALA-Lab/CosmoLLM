#!/usr/bin/env python3

import warnings
from pathlib import Path
from typing import Optional, List
from argparse import ArgumentParser

import numpy as np
import zeus
import matplotlib.pyplot as plt

from models.experiment_config import ExperimentConfig
from parametrization import get_parametrization
from utils.util import get_cosmology, load_model


# TODO: clean up unused code

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


def execute(experiment_path: str) -> None:
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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        'experiment_path',
        help='Path to the experiment results directory, where the chains will be saved',
    )
    args = parser.parse_args()

    # Plot the results
    print("Plotting results...")
    execute(args.experiment_path)
    print("Done!")
