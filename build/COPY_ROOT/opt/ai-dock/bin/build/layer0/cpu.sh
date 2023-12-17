#!/bin/false

build_cpu_main() {
    build_cpu_install_comfyui
}

build_cpu_install_comfyui() {
    /opt/ai-dock/bin/update-comfyui.sh
}

build_cpu_main "$@"