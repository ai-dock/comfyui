#!/bin/false

build_cpu_main() {
    build_cpu_install_deps
    build_common_run_tests
}

build_cpu_install_deps() {
    "$COMFYUI_VENV_PIP" install --no-cache-dir \
        torch==${PYTORCH_VERSION} \
        torchvision \
        torchaudio \
        --extra-index-url=https://download.pytorch.org/whl/cpu
}

build_cpu_main "$@"