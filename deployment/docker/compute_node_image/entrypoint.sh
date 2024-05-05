#!/bin/bash

HOME_DIR=/home/cosmollm

if [ -n "$SSH_PUBLIC_KEY" ]; then
    echo "Setting up SSH public key"

    mkdir -p "$HOME_DIR/.ssh"
    echo "$SSH_PUBLIC_KEY" > "$HOME_DIR/.ssh/authorized_keys"
    chmod 700 "$HOME_DIR/.ssh"
    chmod 600 "$HOME_DIR/.ssh/authorized_keys"

    echo "Changing ownerships..."
    chown -R cosmollm:cosmollm "$HOME_DIR/.ssh"
    echo "Done"
fi

/usr/sbin/sshd -D -e
