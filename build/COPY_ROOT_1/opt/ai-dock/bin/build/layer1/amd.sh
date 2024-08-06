#!/bin/false

build_amd_main() {
    build_amd_install_comfyui
    build_common_run_tests
}

build_amd_install_comfyui() {
    build_common_install_comfyui
}

build_amd_main "$@"