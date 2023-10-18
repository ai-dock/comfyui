#!/bin/false

# This file will be sourced in init.sh

# https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/default.sh
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

## Install custom nodes

# ComfyUI-Manager
comfyui_manager_dir=${nodes_dir}/ComfyUI-Manager
if [[ ! -d $comfyui_manager_dir ]]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager $comfyui_manager_dir
else
    (cd $comfyui_manager_dir && git pull)
fi

## Download checkpoints

# v1-5-pruned-emaonly
model_file=${checkpoints_dir}/v1-5-pruned-emaonly.ckpt
model_url=https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion 1.5...\n"
    download ${model_url} ${model_file}
fi

# v2-1_768-ema-pruned
model_file=${checkpoints_dir}/v2-1_768-ema-pruned.ckpt
model_url=https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion 2.1...\n"
    download ${model_url} ${model_file}
fi

# sd_xl_base_1
model_file=${checkpoints_dir}/sd_xl_base_1.0.safetensors
model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion XL base...\n"
    download ${model_url} ${model_file}
fi

# sd_xl_refiner_1
model_file=${checkpoints_dir}/sd_xl_refiner_1.0.safetensors
model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion XL refiner...\n"
    download ${model_url} ${model_file}
fi

## Download controlnet

model_file=${controlnet_dir}/control_canny-fp16.safetensors
model_url=https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Canny...\n"
    download ${model_url} ${model_file}
fi

## Download loras

# example
#model_file=${loras_dir}/epi_noiseoffset2.safetensors
#model_url=https://civitai.com/api/download/models/16576

#if [[ ! -e ${model_file} ]]; then
#    printf "Downloading epi_noiseoffset2 lora...\n"
#    download ${model_url} ${model_file}
#fi