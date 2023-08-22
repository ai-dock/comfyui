#!/bin/bash

# Must exit and fail to build if any command fails
set -e

bash -c /opt/ai-dock/bin/build/layer0/common.sh

if [[ "$XPU_TARGET" == "NVIDIA_GPU" ]]; then
    bash -c /opt/ai-dock/bin/build/layer0/nvidia.sh
elif [[ "$XPU_TARGET" == "AMD_GPU" ]]; then
    bash -c /opt/ai-dock/bin/build/layer0/amd.sh
elif [[ "$XPU_TARGET" == "CPU" ]]; then
    bash -c /opt/ai-dock/bin/build/layer0/cpu.sh
else
    printf "No valid XPU_TARGET specified\n" >&2
    exit 1
fi

bash -c /opt/ai-dock/bin/build/layer0/clean.sh