#!/bin/false

# This file will be sourced in init.sh

function preflight_main() {
    preflight_move_to_workspace
    preflight_copy_notebook
    preflight_update_comfyui
}

function preflight_move_to_workspace() {
    if [[ $WORKSPACE_MOUNTED = "true" ]]; then
        if [[ ! -d ${WORKSPACE}ComfyUI ]]; then
            mv /opt/ComfyUI ${WORKSPACE}
        fi
            rm -rf /opt/ComfyUI
            ln -s ${WORKSPACE}ComfyUI /opt/ComfyUI
    fi
}

function preflight_copy_notebook() {
    if micromamba env list | grep 'jupyter' > /dev/null 2>&1;  then
        if [[ ! -f "${WORKSPACE}comfyui-service.ipynb" ]]; then
            cp /usr/local/share/ai-dock/comfy-service.ipynb ${WORKSPACE}
        fi
    fi
}

function preflight_update_comfyui() {
    /opt/ai-dock/bin/update-comfyui.sh
}

preflight_main "$@"