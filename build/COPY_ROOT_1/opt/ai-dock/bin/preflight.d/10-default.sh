#!/bin/false

# This file will be sourced in init.sh

function preflight_main() {
    preflight_update_comfyui
    printf "%s" "${COMFYUI_ARGS}" > /etc/comfyui_args.conf
}

function preflight_serverless() {
  printf "Skipping ComfyUI updates in serverless mode\n"
  printf "%s" "${COMFYUI_ARGS}" > /etc/comfyui_args.conf
}

function preflight_update_comfyui() {
    if [[ ${AUTO_UPDATE,,} == "true" ]]; then
        /opt/ai-dock/bin/update-comfyui.sh
    else
        printf "Skipping auto update (AUTO_UPDATE != true)"
    fi
}

# move this to base-image
sudo chown user.ai-dock /var/log/timing_data

if [[ ${SERVERLESS,,} != "true" ]]; then
    preflight_main "$@"
else
   preflight_serverless "$@"
fi