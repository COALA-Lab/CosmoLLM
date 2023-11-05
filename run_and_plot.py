from argparse import ArgumentParser
import os
import subprocess

from models.experiment_config import ExperimentConfig
from utils.util import generate_experiment_id


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('config_path', help="Path to experiment's configuration file")
    parser.add_argument(
        '--results-path',
        help='Path to the results directory, where the chains will be saved',
        default='/tmp/cosmo_llm_results/'
    )
    parser.add_argument('--experiment-id', help='ID of the experiment', default=None)
    parser.add_argument(
        "--workers",
        help="Number of workers to use (must be greater or equal to nchains)", default=-1, type=int
    )
    parser.add_argument(
        '-q', '--quiet',
        help='Turn off the progress bar.', action='store_true', default=False
    )

    # Validate arguments
    args = parser.parse_args()

    config = ExperimentConfig.parse_file(args.config_path)
    if args.workers == -1:
        args.workers = config.nchains
    elif args.workers < config.nchains:
        raise ValueError("Number of workers must be greater or equal to nchains!")

    # Execute the experiment
    experiment_id = args.experiment_id if args.experiment_id else generate_experiment_id()
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONPATH"] = os.getcwd()

    command = (
        f"mpiexec -n {args.workers} python3 executable_scripts/run_experiment.py {args.config_path} "
        f"--results-path {args.results_path} --experiment-id {experiment_id}"
    )
    if args.quiet:
        command += " -q"
    result = subprocess.run(command, shell=True, env=subprocess_env, cwd=os.getcwd())
    if result.returncode != 0:
        raise RuntimeError("Experiment failed!")

    # Plot the results
    command = (
        f"python3 executable_scripts/plot_graphs.py --results-path {args.results_path}/{experiment_id}"
    )
    result = subprocess.run(command, shell=True, env=subprocess_env, cwd=os.getcwd())
    if result.returncode != 0:
        raise RuntimeError("Plotting failed!")

    # TODO: Extract results into csv
    # Add density evaluation with different parameter values

    print("Done!")
