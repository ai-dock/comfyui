#!/bin/false

build_nvidia_main() {
    build_nvidia_install_comfyui
    build_common_run_tests
    build_nvidia_run_tests
}

build_nvidia_install_comfyui() {
    build_common_install_comfyui
}

build_nvidia_run_tests() {
    installed_pytorch_cuda_version=$("$COMFYUI_VENV_PYTHON" -c "import torch; print(torch.version.cuda)")
    if [[ "$CUDA_VERSION" != "$installed_pytorch_cuda"* ]]; then
        echo "Expected PyTorch CUDA ${CUDA_VERSION} but found ${installed_pytorch_cuda}\n"
        exit 1
    fi
}

build_nvidia_main "$@"