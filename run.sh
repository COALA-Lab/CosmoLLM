#!/bin/sh

set -eu

. ./.env

N_PROC=${3:-8}
RESULTS_PATH=$2

EXPERIMENT_UUID=$(python -c "import uuid; print(uuid.uuid4())")

mkdir -p "${RESULTS_PATH}/${EXPERIMENT_UUID}"
cp $1 ${2}/${EXPERIMENT_UUID}/config.json

echo "Running experiment: ${EXPERIMENT_UUID}, with ${N_PROC} MPI processes"
mpiexec -n $N_PROC python run_experiment.py $1 $RESULTS_PATH $EXPERIMENT_UUID


# Plot the graphs
echo "Plotting results at ${RESULTS_PATH}/${EXPERIMENT_UUID}"
python plot_graphs.py ${RESULTS_PATH}/${EXPERIMENT_UUID}

# TODO: Extract results into csv
# Add desnity evaluation with different parameter values
