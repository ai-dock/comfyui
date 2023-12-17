#!/bin/false

build_nvidia_main() {
    build_nvidia_install_comfyui
}

build_nvidia_install_comfyui() {
    micromamba run -n comfyui ${PIP_INSTALL} \
        torch=="${PYTORCH_VERSION}" \
        nvidia-ml-py3
    
    micromamba install -n comfyui -c xformers xformers

    /opt/ai-dock/bin/update-comfyui.sh
}

build_nvidia_main "$@"