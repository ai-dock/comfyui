#!/bin/bash

trap 'kill $(jobs -p)' EXIT

if [[ -z $COMFYUI_PORT ]]; then
    COMFYUI_PORT=8188
fi

printf "Starting ComfyUI...\n"

if [[ $CF_QUICK_TUNNELS = "true" ]]; then
    cloudflared tunnel --url localhost:${COMFYUI_PORT} > /var/log/supervisor/quicktunnel-comfyui.log 2>&1 &
fi

PLATFORM_FLAGS=""
if [[ $XPU_TARGET = "CPU" ]]; then
    PLATFORM_FLAGS="--cpu"
fi
BASE_FLAGS="--listen 0.0.0.0 --port ${COMFYUI_PORT} --disable-auto-launch"

cd /opt/ComfyUI
micromamba run -n comfyui python main.py \
    ${PLATFORM_FLAGS} \
    ${BASE_FLAGS} \
    ${COMFYUI_FLAGS}

