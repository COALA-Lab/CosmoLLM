#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import subprocess
from typing import Optional

from models.experiment_config import ExperimentConfig
from utils.util import generate_experiment_id, load_model


def execute(
        workers: int,
        config_path: str,
        results_path: str,
        experiment_id: Optional[str] = None,
        quiet: bool = False,
) -> None:
    # Validate arguments
    config = load_model(ExperimentConfig, config_path)
    if workers == -1:
        workers = config.nchains
    elif workers < config.nchains:
        raise ValueError("Number of workers must be greater or equal to nchains!")

    experiment_id = experiment_id if experiment_id else generate_experiment_id()

    # Run the experiment
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONPATH"] = os.getcwd()
    subprocess_env["OMPI_ALLOW_RUN_AS_ROOT"] = "1"
    subprocess_env["OMPI_ALLOW_RUN_AS_ROOT_CONFIRM"] = "1"

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

    args = parser.parse_args()

    # Execute the experiment
    execute(
        workers=args.workers,
        config_path=args.config_path,
        results_path=args.results_path,
        experiment_id=args.experiment_id,
        quiet=args.quiet
    )
