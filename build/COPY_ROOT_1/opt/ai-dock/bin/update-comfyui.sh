#!/bin/bash
umask 002

source /opt/ai-dock/bin/venv-set.sh comfyui

if [[ -n "${COMFYUI_REF}" ]]; then
    ref="${COMFYUI_REF}"
else
    # The latest tagged release
    ref="$(curl -s https://api.github.com/repos/comfyanonymous/ComfyUI/tags | \
            jq -r '.[0].name')"
fi

# -r argument has priority
while getopts r: flag
do
    case "${flag}" in
        r) ref="$OPTARG";;
    esac
done

[[ -n $ref ]] || { echo "Failed to get update target"; exit 1; }

printf "Updating ComfyUI (${ref})...\n"

cd /opt/ComfyUI
git fetch --tags
git checkout ${ref}
git pull

"$COMFYUI_VENV_PIP" install --no-cache-dir -r requirements.txt
