#!/bin/bash

trap cleanup EXIT

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
}

function start() {
    source /opt/ai-dock/etc/environment.sh
    if [[ ${SERVERLESS,,} != true ]]; then
        printf "Refusing to start serverless worker without \$SERVERLESS=true\n"
        exec sleep 10
    fi
    
    # Delay launch until workspace is ready
    if [[ -f /run/workspace_sync || -f /run/container_config ]]; then
        while [[ -f /run/workspace_sync || -f /run/container_config ]]; do
            sleep 1
        done
    fi
    printf "Serverless worker started: %s\n" "$(date +"%x %T.%3N")" >> /var/log/timing_data
    
    if [[ -n $RUNPOD_ENDPOINT_ID ]]; then
        printf "Starting RunPod serverless worker...\n"
        micromamba -n serverless run \
            python -u /opt/serverless/providers/runpod/worker.py
    else
        printf "No serverless worker available in this environment"
        exec sleep 10
    fi
}

start 2>&1