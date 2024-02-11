#!/bin/bash

trap cleanup EXIT

LISTEN_PORT=38188
SERVICE_NAME="RunPod Serverless API"

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
}

function start() {
    if [[ ${SERVERLESS,,} = "true" ]]; then
        printf "Refusing to start hosted API service in serverless mode\n"
        exec sleep 10
    fi

    printf "Starting %s...\n" ${SERVICE_NAME}
    
    fuser -k -SIGTERM ${LISTEN_PORT}/tcp > /dev/null 2>&1 &
    wait -n

    cd /opt/serverless/providers/runpod && \
    micromamba run -n serverless python worker.py \
        --rp_serve_api \
        --rp_api_port $LISTEN_PORT \
        --rp_api_host 127.0.0.1
}

start 2>&1