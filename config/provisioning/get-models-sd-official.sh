#!/bin/false

# This file will be sourced in init.sh

# https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/get_model_sd-1.5.sh

# Download Stable Diffusion official models

models_dir=/opt/ComfyUI/models
checkpoints_dir=${models_dir}/checkpoints
vae_dir=${models_dir}/vae
loras_dir=${models_dir}/loras
upscale_dir=${models_dir}/upscale_models

# v1-5-pruned-emaonly
model_file=${checkpoints_dir}/v1-5-pruned-emaonly.ckpt
model_url=https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion 1.5...\n"
    wget -O ${model_file} ${model_url}
fi

# v2-1_768-ema-pruned
model_file=${checkpoints_dir}/v2-1_768-ema-pruned.ckpt
model_url=https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion 2.1...\n"
    wget -O ${model_file} ${model_url}
fi

# sd_xl_base_1
model_file=${checkpoints_dir}/sd_xl_base_1.0.safetensors
model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion XL base...\n"
    wget -O ${model_file} ${model_url}
fi

# sd_xl_refiner_1
model_file=${checkpoints_dir}/sd_xl_refiner_1.0.safetensors
model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors

if [[ ! -e ${model_file} ]]; then
    printf "Downloading Stable Diffusion XL refiner...\n"
    wget -O ${model_file} ${model_url}
fi