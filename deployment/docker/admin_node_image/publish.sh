#!/bin/bash

read -p "Please enter your repository name: " REPO
docker tag cosmollm-admin-node:latest "${REPO}/cosmollm-admin-node:latest"
docker push "${REPO}/cosmollm-admin-node:latest"
