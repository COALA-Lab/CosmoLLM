#!/bin/bash

HOME_DIR=/home/cosmollm

if [ -n "$SSH_PUBLIC_KEY" ]; then
    echo "Setting up SSH public key"

    mkdir -p "$HOME_DIR/.ssh"
    echo "$SSH_PUBLIC_KEY" > "$HOME_DIR/.ssh/id_rsa.pub"
    chmod 700 "$HOME_DIR/.ssh"
    chmod 600 "$HOME_DIR/.ssh/id_rsa.pub"

    echo "Changing ownerships..."
    sudo chown -R cosmollm:cosmollm "$HOME_DIR"
    echo "Done"
fi

if [ -n "$SSH_PRIVATE_KEY" ]; then
    echo "Setting up SSH private key"

    mkdir -p "$HOME_DIR/.ssh"
    echo "$SSH_PRIVATE_KEY" > "$HOME_DIR/.ssh/id_rsa"
    chmod 700 "$HOME_DIR/.ssh"
    chmod 600 "$HOME_DIR/.ssh/id_rsa"

    echo "Changing ownerships..."
    sudo chown -R cosmollm:cosmollm "$HOME_DIR"
    echo "Done"
fi

if [ -n "$MPI_HOSTS" ]; then
    IFS=',' read -ra ADDR <<< "$MPI_HOSTS"

    mkdir -p "$HOME_DIR/.ssh"
    touch "$HOME_DIR/.ssh/known_hosts"
    chmod 700 "$HOME_DIR/.ssh"
    chmod 600 "$HOME_DIR/.ssh/known_hosts"

    echo "Setting up MPI hosts"
    for HOST in "${ADDR[@]}"; do
        echo "Processing $HOST..."
        ssh-keyscan -H $HOST >> ~/.ssh/known_hosts
    done

    echo "Changing ownerships..."
    sudo chown -R cosmollm:cosmollm "$HOME_DIR"
    echo "Done"
fi

cd /app || exit
python3 /app/main.py
