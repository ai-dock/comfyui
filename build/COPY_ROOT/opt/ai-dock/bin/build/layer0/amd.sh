#!/bin/bash

# Must exit and fail to build if any command fails
set -eo pipefail

main() {
    install_comfyui
}

install_comfyui() {
    # Mamba export does not include pip packages.
    # We need to get torch again - todo find a better way?
    micromamba -n comfyui run pip install \
        --no-cache-dir \
        --index-url https://download.pytorch.org/whl/rocm${ROCM_VERSION} \
        torch==${PYTORCH_VERSION} torchvision torchaudio
    /opt/ai-dock/bin/update-comfyui.sh
}

main "$@"; exit