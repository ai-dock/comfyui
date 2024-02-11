#!/bin/bash

# This file will be sourced in init.sh

# https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/animated.sh
printf "\n##############################################\n#                                            #\n#          Provisioning container            #\n#                                            #\n#         This will take some time           #\n#                                            #\n# Your container will be ready on completion #\n#                                            #\n##############################################\n\n"
function download() {
    wget -q --show-progress -e dotbytes="${3:-4M}" -O "$2" "$1"
}

## Set paths
nodes_dir=/opt/ComfyUI/custom_nodes
models_dir=/opt/ComfyUI/models
checkpoints_dir=${models_dir}/checkpoints
vae_dir=${models_dir}/vae
controlnet_dir=${models_dir}/controlnet
loras_dir=${models_dir}/loras
upscale_dir=${models_dir}/upscale_models

### Install custom nodes

# ComfyUI-Manager
this_node_dir=${nodes_dir}/ComfyUI-Manager
if [[ ! -d $this_node_dir ]]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager $this_node_dir
else
    (cd $this_node_dir && git pull)
fi

# ComfyUI-AnimateDiff-Evolved
this_node_dir=${nodes_dir}/ComfyUI-AnimateDiff-Evolved
if [[ ! -d $this_node_dir ]]; then
    git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved $this_node_dir
else
    (cd $this_node_dir && git pull)
fi

animated_models_dir=${nodes_dir}/ComfyUI-AnimateDiff-Evolved/models

# ComfyUI-Advanced-ControlNet
this_node_dir=${nodes_dir}/ComfyUI-Advanced-ControlNet
if [[ ! -d $this_node_dir ]]; then
    git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet $this_node_dir
else
    (cd $this_node_dir && git pull)
fi

### Download checkpoints

## Animated
# mm_sd_v15
model_file=${animated_models_dir}/mm_sd_v15.ckpt
model_url=https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15.ckpt
if [[ ! -e ${model_file} ]]; then
    printf "mm_sd_v15.ckpt...\n"
    download ${model_url} ${model_file}
fi

## Standard
# v1-5-pruned-emaonly
model_file=${checkpoints_dir}/v1-5-pruned-emaonly.ckpt
model_url=https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion 1.5...\n"
    download ${model_url} ${model_file}
fi

### Download controlnet

## example

#model_file=${controlnet_dir}/control_canny-fp16.safetensors
#model_url=https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors

#if [[ ! -e ${model_file} ]]; then
#    printf "Downloading Canny...\n"
#    download ${model_url} ${model_file}
#fi

### Download loras

## example

#model_file=${loras_dir}/epi_noiseoffset2.safetensors
#model_url=https://civitai.com/api/download/models/16576

#if [[ ! -e ${model_file} ]]; then
#    printf "Downloading epi_noiseoffset2 lora...\n"
#    download ${model_url} ${model_file}
#fi