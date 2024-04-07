#!/bin/bash

read -p "Please enter your repository name: " REPO
docker tag cosmollm-compute-node:latest "${REPO}/cosmollm-compute-node:latest"
docker push "${REPO}/cosmollm-compute-node:latest"
