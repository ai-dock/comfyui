#!/bin/false

# This file will be sourced in init.sh

function preflight_main() {
    preflight_copy_notebook
    preflight_update_comfyui
}

function preflight_serverless() {
  printf "Refusing to update ComfyUI in serverless mode\n \
    Nothing to do. \n"
}

function preflight_copy_notebook() {
    if micromamba env list | grep 'jupyter' > /dev/null 2>&1;  then
        if [[ ! -f "${WORKSPACE}comfyui.ipynb" ]]; then
            cp /usr/local/share/ai-dock/comfyui.ipynb ${WORKSPACE}
        fi
    fi
}

function preflight_update_comfyui() {
    /opt/ai-dock/bin/update-comfyui.sh
}

if [[ ${SERVERLESS,,} != "true" ]]; then
    preflight_main "$@"
else
   preflight_serverless "$@"
fi