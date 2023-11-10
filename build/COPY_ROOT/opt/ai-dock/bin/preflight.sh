#!/bin/false

# This file will be sourced in init.sh

function preflight_main() {
    preflight_copy_notebook
    preflight_link_baked_models
    preflight_update_comfyui
    printf "%s" "${COMFYUI_FLAGS}" > /etc/comfyui_flags.conf
}

function preflight_serverless() {
  printf "Refusing to update ComfyUI in serverless mode\n"
  preflight_link_baked_models
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

# Baked in models cannot exist in /opt/ComfyUI or they will sync with volume mounts
# We don't want that, so they live in /opt/model_repository and get symlinked at runtime
# We force this, because loading from volumes will always be slower, so let's avoid having them there

function preflight_link_baked_models() {
    for file in /opt/model_repository/checkpoints/*; do
        ln -sf "$file" "${WORKSPACE}ComfyUI/models/checkpoints/"
    done
    for file in /opt/model_repository/controlnet/*; do
        ln -sf "$file" "${WORKSPACE}ComfyUI/models/controlnet/"
    done
    for file in /opt/model_repository/esrgan/*; do
        ln -sf "$file" "${WORKSPACE}ComfyUI/models/upscale_models/"
    done
    for file in /opt/model_repository/lora/*; do
        ln -sf "$file" "${WORKSPACE}ComfyUI/models/loras/"
    done
    for file in /opt/model_repository/vae/*; do
        ln -sf "$file" "${WORKSPACE}ComfyUI/models/vae/"
    done
}

if [[ ${SERVERLESS,,} != "true" ]]; then
    preflight_main "$@"
else
   preflight_serverless "$@"
fi