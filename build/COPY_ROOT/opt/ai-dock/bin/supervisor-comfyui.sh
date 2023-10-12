#!/bin/bash

trap cleanup EXIT

LISTEN_PORT=1818
METRICS_PORT=1918
PROXY_SECURE=true

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
    rm /run/http_ports/$PROXY_PORT > /dev/null 2>&1
}

if [[ -z $COMFYUI_PORT ]]; then
    COMFYUI_PORT=8188
fi

PROXY_PORT=$COMFYUI_PORT
SERVICE_NAME="ComfyUI"

file_content=$(
  jq --null-input \
    --arg listen_port "${LISTEN_PORT}" \
    --arg metrics_port "${METRICS_PORT}" \
    --arg proxy_port "${PROXY_PORT}" \
    --arg proxy_secure "${PROXY_SECURE,,}" \
    --arg service_name "${SERVICE_NAME}" \
    '$ARGS.named'
)

printf "%s" $file_content > /run/http_ports/$PROXY_PORT

PLATFORM_FLAGS=""
if [[ $XPU_TARGET = "CPU" ]]; then
    PLATFORM_FLAGS="--cpu"
fi

BASE_FLAGS="--listen 127.0.0.1 --port ${LISTEN_PORT} --disable-auto-launch"

# Delay launch until micromamba is ready
if [[ -f /run/workspace_moving || -f /run/provisioning_script ]]; then
    /usr/bin/python3 /opt/ai-dock/fastapi/logviewer/main.py \
        -p $LISTEN_PORT \
        -r 5 \
        -s "${SERVICE_NAME}" \
        -t "Preparing ${SERVICE_NAME}" &
    fastapi_pid=$!
    
    while [[ -f /run/workspace_moving || -f /run/provisioning_script ]]; do
        sleep 1
    done
    
    printf "\nStarting %s... " ${SERVICE_NAME:-service}
    kill $fastapi_pid &
    wait -n
    printf "OK\n"
else
    printf "Starting %s...\n" ${SERVICE_NAME}
fi

kill -9 $(lsof -t -i:$LISTEN_PORT) > /dev/null 2>&1 &
wait -n

cd /opt/ComfyUI
micromamba run -n comfyui python main.py \
    ${PLATFORM_FLAGS} \
    ${BASE_FLAGS} \
    ${COMFYUI_FLAGS}
