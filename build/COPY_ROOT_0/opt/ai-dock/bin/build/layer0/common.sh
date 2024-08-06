#!/bin/false

source /opt/ai-dock/etc/environment.sh

build_common_main() {
    build_common_create_venv
}

build_common_create_venv() {
    apt-get update
    $APT_INSTALL \
        "python${PYTHON_VERSION}" \
        "python${PYTHON_VERSION}-dev" \
        "python${PYTHON_VERSION}-venv"

    # ComfyUI venv
    "python${PYTHON_VERSION}" -m venv "$COMFYUI_VENV"
    "$COMFYUI_VENV_PIP" install --no-cache-dir \
        ipykernel \
        ipywidgets
    "$COMFYUI_VENV_PYTHON" -m ipykernel install \
        --name="comfyui" \
        --display-name="Python${PYTHON_VERSION} (comfyui)"
    # Add the default Jupyter kernel as an alias of comfyui
    "$COMFYUI_VENV_PYTHON" -m ipykernel install \
        --name="python3" \
        --display-name="Python3 (ipykernel)"
    
    # API venv
    "python${PYTHON_VERSION}" -m venv "$API_VENV"
    "$API_VENV_PIP" install --no-cache-dir \
        ipykernel \
        ipywidgets
    "$API_VENV_PYTHON" -m ipykernel install \
        --name="api-wrapper" \
        --display-name="Python${PYTHON_VERSION} (api-wrapper)"
}


build_common_run_tests() {
    installed_pytorch_version=$("$COMFYUI_VENV_PYTHON" -c "import torch; print(torch.__version__)")
    if [[ "$installed_pytorch_version" != "$PYTORCH_VERSION"* ]]; then
        echo "Expected PyTorch ${PYTORCH_VERSION} but found ${installed_pytorch_version}\n"
        exit 1
    fi
}

build_common_main "$@"