#!/bin/false

build_amd_main() {
    build_amd_install_deps
    build_common_run_tests
}

build_amd_install_deps() {
    "$COMFYUI_VENV_PIP" install --no-cache-dir \
        torch==${PYTORCH_VERSION} \
        torchvision \
        torchaudio \
        --index-url=https://download.pytorch.org/whl/rocm${ROCM_VERSION}
}

build_amd_main "$@"