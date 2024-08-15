#!/bin/bash

trap cleanup EXIT

LISTEN_PORT=${COMFYUI_PORT_LOCAL:-18188}
METRICS_PORT=${COMFYUI_METRICS_PORT:-28188}
SERVICE_URL="${COMFYUI_URL:-}"
QUICKTUNNELS=true

function cleanup() {
    kill $(jobs -p) > /dev/null 2>&1
    rm /run/http_ports/$PROXY_PORT > /dev/null 2>&1
    fuser -k -SIGTERM ${LISTEN_PORT}/tcp > /dev/null 2>&1 &
    wait -n
}

function start() {
    source /opt/ai-dock/etc/environment.sh
    source /opt/ai-dock/bin/venv-set.sh serviceportal
    source /opt/ai-dock/bin/venv-set.sh comfyui

    if [[ ! -v COMFYUI_PORT || -z $COMFYUI_PORT ]]; then
        COMFYUI_PORT=${COMFYUI_PORT_HOST:-8188}
    fi
    PROXY_PORT=$COMFYUI_PORT
    SERVICE_NAME="ComfyUI"
    
    file_content="$(
      jq --null-input \
        --arg listen_port "${LISTEN_PORT}" \
        --arg metrics_port "${METRICS_PORT}" \
        --arg proxy_port "${PROXY_PORT}" \
        --arg proxy_secure "${PROXY_SECURE,,}" \
        --arg service_name "${SERVICE_NAME}" \
        --arg service_url "${SERVICE_URL}" \
        '$ARGS.named'
    )"
    
    printf "%s" "$file_content" > /run/http_ports/$PROXY_PORT
    
    PLATFORM_ARGS=""
    if [[ $XPU_TARGET = "CPU" ]]; then
        PLATFORM_ARGS="--cpu"
    fi
    
    BASE_ARGS="--disable-auto-launch"
    
    # Delay launch until venv is ready
    if [[ -f /run/workspace_sync || -f /run/container_config ]]; then
        if [[ ${SERVERLESS,,} != "true" ]]; then
            printf "Waiting for workspace sync...\n"
            fuser -k -SIGKILL ${LISTEN_PORT}/tcp > /dev/null 2>&1 &
            wait -n
            "$SERVICEPORTAL_VENV_PYTHON" /opt/ai-dock/fastapi/logviewer/main.py \
                -p $LISTEN_PORT \
                -r 5 \
                -s "${SERVICE_NAME}" \
                -t "Preparing ${SERVICE_NAME}" &
            fastapi_pid=$!
            
            while [[ -f /run/workspace_sync || -f /run/container_config ]]; do
                sleep 1
            done
            
            kill $fastapi_pid &
            wait -n
        else
            printf "Waiting for workspace symlinks and pre-flight checks...\n"
            while [[ -f /run/workspace_sync || -f /run/container_config ]]; do
                sleep 1
            done
        fi
    fi
    
    printf "%s started: %s\n" "${SERVICE_NAME}" "$(date +"%x %T.%3N")" >> /var/log/timing_data
    printf "Starting %s...\n" "${SERVICE_NAME}"
    
    fuser -k -SIGKILL ${LISTEN_PORT}/tcp > /dev/null 2>&1 &
    wait -n

    ARGS_COMBINED="${PLATFORM_ARGS} ${BASE_ARGS} $(cat /etc/comfyui_args.conf)"
    printf "Starting %s...\n" "${SERVICE_NAME}"

    cd /opt/ComfyUI
    source "$COMFYUI_VENV/bin/activate"
    LD_PRELOAD=libtcmalloc.so \
        python main.py \
        ${ARGS_COMBINED} --port ${LISTEN_PORT}
}

start 2>&1