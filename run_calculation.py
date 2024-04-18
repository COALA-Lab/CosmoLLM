#!/usr/bin/env python3
import tempfile
from argparse import ArgumentParser
import os
import subprocess
from typing import Optional

import settings
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
    extra_env_vars = {
        "PYTHONPATH": os.getcwd(),
        "OMPI_ALLOW_RUN_AS_ROOT": "1",
        "OMPI_ALLOW_RUN_AS_ROOT_CONFIRM": "1",
    }
    subprocess_env.update(extra_env_vars)

    mpi_arguments = ""
    hostfile = None
    if settings.MPI_HOSTS:
        workers = len(settings.MPI_HOSTS) * settings.MPI_HOST_SLOTS

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            hostfile = temp_file.name

            for host in settings.MPI_HOSTS:
                temp_file.write(f"{host} slots={settings.MPI_HOST_SLOTS}\n".encode())
        if not hostfile:
            raise RuntimeError("Failed to create hostfile!")

        mpi_arguments += f"--hostfile {hostfile} "

        for key, value in extra_env_vars.items():
            mpi_arguments += f"-x {key}={value} "

        mpi_arguments += "--use-hwthread-cpus -nolocal --map-by slot "

    mpi_arguments += f"-n {workers} "
    mpi_command = f"mpiexec " + mpi_arguments
    cosmollm_command = (
        f"python3 executable_scripts/run_experiment.py {config_path} "
        f"--results-path {results_path} --experiment-id {experiment_id} "
    )
    if quiet:
        cosmollm_command += " -q"

    command = mpi_command + cosmollm_command
    result = subprocess.run(command, shell=True, env=subprocess_env, cwd=os.getcwd())

    if hostfile:
        os.remove(hostfile)

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
