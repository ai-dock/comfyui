#!/bin/false

source /opt/ai-dock/etc/environment.sh

build_common_main() {
    build_common_create_env
    build_common_install_jupyter_kernels
}

build_common_create_env() {
    apt-get update
    $APT_INSTALL \
        libgl1-mesa-glx \
        libtcmalloc-minimal4

    ln -sf $(ldconfig -p | grep -Po "libtcmalloc_minimal.so.\d" | head -n 1) \
        /lib/x86_64-linux-gnu/libtcmalloc.so
    
    micromamba create -n comfyui
    micromamba run -n comfyui mamba-skel
    micromamba install -n comfyui -y \
        python="${PYTHON_VERSION}" \
        ipykernel \
        ipywidgets \
        nano
    micromamba run -n comfyui install-pytorch -v "$PYTORCH_VERSION"

    # RunPod serverless support
    micromamba create -n serverless 
    micromamba run -n serverless mamba-skel
    micromamba install -n serverless \
        python=3.10 \
        python-magic \
        ipykernel \
        ipywidgets \
        nano
    micromamba run -n serverless $PIP_INSTALL \
        runpod
}


build_common_install_jupyter_kernels() {
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
}

build_common_install_comfyui() {
    # Set git SHA to latest if not provided
    if [[ -z $COMFYUI_SHA ]]; then
        export COMFYUI_SHA="$(curl -fsSL "https://api.github.com/repos/comfyanonymous/ComfyUI/commits/master" \
        | jq -r '.sha[0:7]')"
        env-store COMFYUI_SHA
    fi

    cd /opt
    git clone https://github.com/comfyanonymous/ComfyUI
    cd /opt/ComfyUI
    git checkout "$COMFYUI_SHA"

    micromamba run -n comfyui ${PIP_INSTALL} -r requirements.txt
}

build_common_run_tests() {
    installed_pytorch_version=$(micromamba run -n comfyui python -c "import torch; print(torch.__version__)")
    if [[ "$installed_pytorch_version" != "$PYTORCH_VERSION"* ]]; then
        echo "Expected PyTorch ${PYTORCH_VERSION} but found ${installed_pytorch_version}\n"
        exit 1
    fi
}

build_common_main "$@"