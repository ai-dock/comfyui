#!/bin/false

# This file will be sourced in init.sh

function preflight_main() {
    preflight_move_to_workspace
    preflight_copy_notebook
    preflight_update_comfyui
}

function preflight_move_to_workspace() {
    if [[ ! -e ${WORKSPACE}ComfyUI && -d /opt/ComfyUI ]]; then
        if [[ $WORKSPACE_MOUNTED = "true" ]]; then
            mv /opt/ComfyUI ${WORKSPACE}
            ln -s ${WORKSPACE}ComfyUI /opt/ComfyUI
        else
             ln -s /opt/ComfyUI ${WORKSPACE}ComfyUI
         fi
    fi
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

preflight_main "$@"