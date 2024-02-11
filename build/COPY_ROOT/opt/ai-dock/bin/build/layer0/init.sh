#!/bin/bash

# Must exit and fail to build if any command fails
set -eo pipefail
umask 002

source /opt/ai-dock/bin/build/layer0/common.sh

if [[ "$XPU_TARGET" == "NVIDIA_GPU" ]]; then
    source /opt/ai-dock/bin/build/layer0/nvidia.sh
elif [[ "$XPU_TARGET" == "AMD_GPU" ]]; then
    source /opt/ai-dock/bin/build/layer0/amd.sh
elif [[ "$XPU_TARGET" == "CPU" ]]; then
    source /opt/ai-dock/bin/build/layer0/cpu.sh
else
    printf "No valid XPU_TARGET specified\n" >&2
    exit 1
fi

$MAMBA_DEFAULT_RUN python /opt/ai-dock/tests/assert-torch-version.py

source /opt/ai-dock/bin/build/layer0/clean.sh