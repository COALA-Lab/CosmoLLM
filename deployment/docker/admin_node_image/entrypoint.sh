#!/bin/bash

HOME_DIR=/home/cosmollm

if [ -n "$KUBE_CONFIG" ]; then
    echo "Setting up kube config"

    mkdir -p "$HOME_DIR/.kube"
    echo "$KUBE_CONFIG" > "$HOME_DIR/.kube/config"
    chmod 700 "$HOME_DIR/.kube"
    chmod 600 "$HOME_DIR/.kube/config"

    echo "Changing ownerships..."
    chown -R cosmollm:cosmollm "$HOME_DIR/.kube"
    echo "Done"
else
    echo "KUBE_CONFIG is not set!"
    exit 1
fi

cd /app || exit
python3 /app/main.py --admin
