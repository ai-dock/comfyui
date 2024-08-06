#!/bin/bash

trap cleanup EXIT

LISTEN_PORT=38188
SERVICE_NAME="ComfyUI API Wrapper"

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
    fuser -k -SIGTERM ${LISTEN_PORT}/tcp > /dev/null 2>&1 &
    wait -n
}

function start() {
    source /opt/ai-dock/etc/environment.sh
    source /opt/ai-dock/bin/venv-set.sh api

    printf "Starting %s...\n" ${SERVICE_NAME}
    
    fuser -k -SIGKILL ${LISTEN_PORT}/tcp > /dev/null 2>&1 &
    wait -n

    cd /opt/ai-dock/api-wrapper && \
    source "$API_VENV/bin/activate"
    uvicorn main:app \
        --host 127.0.0.1 \
        --port $LISTEN_PORT \
        --reload
}

start 2>&1