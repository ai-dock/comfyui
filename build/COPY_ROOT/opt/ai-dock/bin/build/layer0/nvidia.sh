#!/bin/false

build_nvidia_main() {
    build_nvidia_install_comfyui
    build_common_run_tests
    build_nvidia_run_tests
}

build_nvidia_install_comfyui() {
    micromamba run -n comfyui ${PIP_INSTALL} \
        nvidia-ml-py3
    
    micromamba install -n comfyui -c xformers -y \
        xformers \
        pytorch=${PYTORCH_VERSION} \
        pytorch-cuda="$(cut -d '.' -f 1,2 <<< "${CUDA_VERSION}")"

    build_common_install_comfyui
}

build_nvidia_run_tests() {
    installed_pytorch_cuda_version=$(micromamba run -n comfyui python -c "import torch; print(torch.version.cuda)")
    if [[ "$CUDA_VERSION" != "$installed_pytorch_cuda"* ]]; then
        echo "Expected PyTorch CUDA ${CUDA_VERSION} but found ${installed_pytorch_cuda}\n"
        exit 1
    fi
}

build_nvidia_main "$@"