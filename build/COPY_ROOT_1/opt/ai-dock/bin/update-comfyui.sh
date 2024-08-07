#!/bin/bash

branch=master

if [[ -n "${COMFYUI_BRANCH}" ]]; then
    branch="${COMFYUI_BRANCH}"
fi

# -b flag has priority
while getopts b: flag
do
    case "${flag}" in
        b) branch="$OPTARG";;
    esac
done

printf "Updating ComfyUI (${branch})...\n"

cd /opt/ComfyUI
git checkout ${branch}
git pull

"$COMFYUI_VENV_PIP" install --no-cache-dir \
    -r requirements.txt
