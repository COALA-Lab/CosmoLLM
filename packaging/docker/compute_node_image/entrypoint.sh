#!/bin/bash

if [ -n "$SSH_PUBLIC_KEY" ]; then
    echo "Setting up SSH public key"

    HOME_DIR=/home/cosmollm

    mkdir -p "$HOME_DIR/.ssh"
    echo "$SSH_PUBLIC_KEY" > "$HOME_DIR/.ssh/authorized_keys"
    chmod 700 "$HOME_DIR/.ssh"
    chmod 600 "$HOME_DIR/.ssh/authorized_keys"
    chown -R cosmollm:cosmollm "$HOME_DIR"
fi

/usr/sbin/sshd -D -e
