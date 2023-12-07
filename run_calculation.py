#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import subprocess

from models.experiment_config import ExperimentConfig
from utils.util import generate_experiment_id, load_model


def execute(workers: int, config_path: str, results_path: str, experiment_id: str, quiet: bool) -> None:
    # Run the experiment
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONPATH"] = os.getcwd()

    command = (
        f"mpiexec -n {workers} python3 executable_scripts/run_experiment.py {config_path} "
        f"--results-path {results_path} --experiment-id {experiment_id}"
    )
    if quiet:
        command += " -q"
    result = subprocess.run(command, shell=True, env=subprocess_env, cwd=os.getcwd())
    if result.returncode != 0:
        raise RuntimeError("Experiment failed!")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--config_path',
        help="Path to the experiment's configuration file",
        default='configs/config_quadratic_density.json'
    )
    parser.add_argument(
        '-r', '--results-path',
        help='Path to the results directory, where the chains will be saved',
        default='/tmp/cosmo_llm_results/'
    )
    parser.add_argument(
        '-i', '--experiment-id',
        help='ID of the experiment',
        default=generate_experiment_id()
    )
    parser.add_argument(
        '-n', '--workers',
        help="Number of workers to use (must be greater or equal to nchains)",
        default=-1,
        type=int
    )
    parser.add_argument(
        '-q', '--quiet',
        help='Turn off the progress bar.', action='store_true', default=False
    )

    # Validate arguments
    args = parser.parse_args()

    config = load_model(ExperimentConfig, args.config_path)
    if args.workers == -1:
        args.workers = config.nchains
    elif args.workers < config.nchains:
        raise ValueError("Number of workers must be greater or equal to nchains!")

    experiment_id = args.experiment_id if args.experiment_id else generate_experiment_id()

    # Execute the experiment
    execute(
        workers=args.workers,
        config_path=args.config_path,
        results_path=args.results_path,
        experiment_id=experiment_id,
        quiet=args.quiet
    )
