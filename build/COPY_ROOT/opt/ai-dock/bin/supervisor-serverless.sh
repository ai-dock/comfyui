#!/bin/bash

trap cleanup EXIT

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
}

function start() {
    if [[ ${SERVERLESS,,} != true ]]; then
        printf "Refusing to start serverless worker without \$SERVERLESS=true\n"
        exec sleep 10
    fi
    
    # Delay launch until workspace is ready
    # This should never happen - Don't sync on serverless!
    if [[ -f /run/workspace_sync || -f /run/container_config ]]; then
        while [[ -f /run/workspace_sync || -f /run/container_config ]]; do
            sleep 1
        done
    fi
    printf "Serverless worker started: %s\n" "$(date +"%x %T.%3N")" >> /var/log/timing_data
    printf "Starting %s serverless worker...\n" ${CLOUD_PROVIDER}
    
    if [[ ${CLOUD_PROVIDER} = "runpod.io" ]]; then
        exec micromamba -n serverless run \
            python -u /opt/serverless/providers/runpod/worker.py
    else
        printf "No serverless worker available in this environment"
        exec sleep 10
    fi
}

start 2>&1