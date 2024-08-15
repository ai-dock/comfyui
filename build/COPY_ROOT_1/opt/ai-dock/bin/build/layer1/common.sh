#!/bin/false

source /opt/ai-dock/etc/environment.sh

build_common_main() {
    build_common_install_api
}

build_common_install_api() {
    # ComfyUI API wrapper
    $APT_INSTALL libmagic1
    $API_VENV_PIP install --no-cache-dir \
        -r /opt/ai-dock/api-wrapper/requirements.txt

}

build_common_install_comfyui() {
    # Set to latest release if not provided
    if [[ -z $COMFYUI_BUILD_REF ]]; then
        export COMFYUI_BUILD_REF="$(curl -s https://api.github.com/repos/comfyanonymous/ComfyUI/tags | \
            jq -r '.[0].name')"
        env-store COMFYUI_BUILD_REF
    fi

    cd /opt
    git clone https://github.com/comfyanonymous/ComfyUI
    cd /opt/ComfyUI
    git checkout "$COMFYUI_BUILD_REF"

    $COMFYUI_VENV_PIP install --no-cache-dir \
        -r requirements.txt
}

build_common_run_tests() {
    installed_pytorch_version=$("$COMFYUI_VENV_PYTHON" -c "import torch; print(torch.__version__)")
    if [[ "$installed_pytorch_version" != "$PYTORCH_VERSION"* ]]; then
        echo "Expected PyTorch ${PYTORCH_VERSION} but found ${installed_pytorch_version}\n"
        exit 1
    fi
}

build_common_main "$@"