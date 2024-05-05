#!/bin/bash

read -p "Please enter your repository name: " REPO
docker tag cosmollm:latest "${REPO}/cosmollm:latest"
docker push "${REPO}/cosmollm:latest"
