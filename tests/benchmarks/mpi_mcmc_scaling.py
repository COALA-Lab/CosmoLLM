import os
import time
import statistics
import sys
from argparse import ArgumentParser
from typing import Callable

sys.path.append(os.getcwd())

from run_calculation import execute as mcmc_execute


def record_times(repeats: int, method: Callable):
    times = []

    for i in range(repeats):
        print(f"Running experiment {i + 1}/{repeats}")
        print()
        start_time = time.time()
        method()
        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        print(f"Experiment {i + 1} took {elapsed_time:.6f} seconds end-to-end\n")

    average_time = statistics.mean(times)
    print(f"Average end-to-end time: {average_time:.6f} seconds")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '-r', '--repeats',
        help='Number of times to repeat the experiment',
        default=10,
        type=int
    )
    parser.add_argument(
        '-w', '--workers',
        help='Number of workers to use (must be greater or equal to nchains)',
        default=-1,
        type=int
    )
    parser.add_argument(
        '-c', '--config-path',
        help="Path to the experiment's configuration file",
        default='configs/config_quadratic_density.json'
    )

    args = parser.parse_args()
    repeats = args.repeats
    workers = args.workers
    config_path = args.config_path

    record_times(repeats, lambda: mcmc_execute(workers, config_path, results_path="/tmp", quiet=False))
