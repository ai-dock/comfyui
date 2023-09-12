#!/bin/bash

trap cleanup EXIT

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
    rm /run/http_ports/$PORT > /dev/null 2>&1
}

SERVICE="ComfyUI"

if [[ -z $COMFYUI_PORT ]]; then
    COMFYUI_PORT=8188
fi

PORT=$COMFYUI_PORT
METRICS_PORT=1188
SERVICE_NAME="ComfyUI"

printf "{\"port\": \"$PORT\", \"metrics_port\": \"$METRICS_PORT\", \"service_name\": \"$SERVICE_NAME\"}" > /run/http_ports/$PORT

PLATFORM_FLAGS=""
if [[ $XPU_TARGET = "CPU" ]]; then
    PLATFORM_FLAGS="--cpu"
fi
BASE_FLAGS="--listen 0.0.0.0 --port ${COMFYUI_PORT} --disable-auto-launch"

if [[ -f /run/provisioning_script ]]; then
    micromamba run -n fastapi python /opt/ai-dock/fastapi/logviewer/main.py \
        -p $COMFYUI_PORT \
        -r 5 \
        -s ${SERVICE} \
        -u comfyui \
        -t "Preparing ${SERVICE}" &
    fastapi_pid=$!
    
    while [[ -f /run/provisioning_script ]]; do
        sleep 1
    done
    
    printf "\nStarting %s... " ${SERVICE:-service}
    kill $fastapi_pid && \
    printf "OK\n"
else
    printf "Starting %s...\n" ${SERVICE}
fi

kill -9 $(lsof -t -i:$COMFYUI_PORT) > /dev/null 2>&1 &
wait -n

cd /opt/ComfyUI
micromamba run -n comfyui python main.py \
    ${PLATFORM_FLAGS} \
    ${BASE_FLAGS} \
    ${COMFYUI_FLAGS}

