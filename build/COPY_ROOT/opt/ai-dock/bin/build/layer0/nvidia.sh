#!/bin/bash

# Must exit and fail to build if any command fails
set -eo pipefail

main() {
    install_comfyui
}

install_comfyui() {
    micromamba run -n comfyui ${PIP_INSTALL} \
        torch=="${PYTORCH_VERSION}" \
        nvidia-ml-py3
    
    micromamba install -n comfyui -c xformers xformers

    /opt/ai-dock/bin/update-comfyui.sh
}

main "$@"; exit