#!/bin/false

# This file will be sourced in init.sh

function preflight_main() {
    preflight_copy_notebook
    preflight_update_comfyui
    printf "%s" "${COMFYUI_FLAGS}" > /etc/comfyui_flags.conf
}

function preflight_serverless() {
  printf "Skipping ComfyUI updates in serverless mode\n"
  printf "%s" "${COMFYUI_FLAGS}" > /etc/comfyui_flags.conf
}

function preflight_copy_notebook() {
    if micromamba env list | grep 'jupyter' > /dev/null 2>&1;  then
        if [[ ! -f "${WORKSPACE}comfyui.ipynb" ]]; then
            cp /usr/local/share/ai-dock/comfyui.ipynb ${WORKSPACE}
        fi
    fi
}

function preflight_update_comfyui() {
    if [[ ${AUTO_UPDATE,,} != "false" ]]; then
        /opt/ai-dock/bin/update-comfyui.sh
    else
        printf "Skipping auto update (AUTO_UPDATE=false)"
    fi
}

# move this to base-image
sudo chown user.ai-dock /var/log/timing_data

if [[ ${SERVERLESS,,} != "true" ]]; then
    preflight_main "$@"
else
   preflight_serverless "$@"
fi