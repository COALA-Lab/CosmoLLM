#!/bin/bash

read -p "Please enter your OpenAI API key: " KEY
docker build -t cosmollm:latest --build-arg "OPENAI_API_KEY=$KEY" .
