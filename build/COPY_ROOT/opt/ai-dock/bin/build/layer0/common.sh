#!/bin/bash

# Must exit and fail to build if any command fails
set -eo pipefail

comfyui_git="https://github.com/comfyanonymous/ComfyUI"

main() {
    create_env
    install_jupyter_kernels
    clone_comfyui
}

create_env() {
    apt-get update
    $APT_INSTALL libgl1 \
        libgoogle-perftools4

    ln -sf $(ldconfig -p | grep -Po "libtcmalloc.so.\d" | head -n 1) \
        /lib/x86_64-linux-gnu/libtcmalloc.so

    # A new pytorch env costs ~ 300Mb
    exported_env=/tmp/${MAMBA_DEFAULT_ENV}.yaml
    micromamba env export -n ${MAMBA_DEFAULT_ENV} > "${exported_env}"
    $MAMBA_CREATE -n comfyui --file "${exported_env}"
    
    # RunPod serverless support
    $MAMBA_CREATE -n serverless -c defaults python=3.10
    micromamba run -n serverless $PIP_INSTALL \
        runpod
}


install_jupyter_kernels() {
    if [[ $IMAGE_BASE =~ "jupyter-pytorch" ]]; then
        $MAMBA_INSTALL -n comfyui -c defaults -y \
            ipykernel \
            ipywidgets
        
        kernel_path=/usr/local/share/jupyter/kernels
        
        # Add the often-present "Python3 (ipykernel) as a comfyui alias"
        rm -rf ${kernel_path}/python3
        dir="${kernel_path}/python3"
        file="${dir}/kernel.json"
        cp -rf ${kernel_path}/../_template ${dir}
        sed -i 's/DISPLAY_NAME/'"Python3 (ipykernel)"'/g' ${file}
        sed -i 's/PYTHON_MAMBA_NAME/'"comfyui"'/g' ${file}
        
        dir="${kernel_path}/comfyui"
        file="${dir}/kernel.json"
        cp -rf ${kernel_path}/../_template ${dir}
        sed -i 's/DISPLAY_NAME/'"ComfyUI"'/g' ${file}
        sed -i 's/PYTHON_MAMBA_NAME/'"comfyui"'/g' ${file}
        
        dir="${kernel_path}/serverless"
        file="${dir}/kernel.json"
        cp -rf ${kernel_path}/../_template ${dir}
        sed -i 's/DISPLAY_NAME/'"Serverless"'/g' ${file}
        sed -i 's/PYTHON_MAMBA_NAME/'"serverless"'/g' ${file}
    fi
}

clone_comfyui() {
    cd /opt
    git clone ${comfyui_git}
}

main "$@"; exit