#!/bin/bash

export PYTHONPATH=$PYTHONPATH:$(pwd)

for test in tests/*.py; do
    python3 $test
done
