#!/bin/bash

# This file will be sourced in init.sh

# https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/seargedp-seargesdxl.sh

# Download SeargeSDXL and the required model files if they do not already exist

searge_git="https://github.com/SeargeDP/SeargeSDXL"
searge_dir="/opt/ComfyUI/custom_nodes/SeargeSDXL"

models_dir=/opt/ComfyUI/models
checkpoints_dir=${models_dir}/checkpoints
vae_dir=${models_dir}/vae
loras_dir=${models_dir}/loras
upscale_dir=${models_dir}/upscale_models

base_model_file=${checkpoints_dir}/sd_xl_base_1.0.safetensors
base_model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
refiner_model_file=${checkpoints_dir}/sd_xl_refiner_1.0.safetensors
refiner_model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
sdxl_vae_file=${vae_dir}/sdxl_vae.safetensors
sdxl_vae_url=https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors
offset_lora_file=${loras_dir}/sd_xl_offset_example-lora_1.0.safetensors
offset_lora_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_offset_example-lora_1.0.safetensors
siax_upscale_file=${upscale_dir}/4x_NMKD-Siax_200k.pth
siax_upscale_url=https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x_NMKD-Siax_200k.pth
ultrasharp_upscale_file=${upscale_dir}/4x-UltraSharp.pth
ultrasharp_upscale_url=https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x-UltraSharp.pth

if [[ ! -d $searge_dir ]]; then
    git clone https://github.com/SeargeDP/SeargeSDXL $searge_dir
else
    cd $searge_dir && git pull
fi

if [[ ! -f ${base_model_file} ]]; then
    wget -O ${base_model_file} ${base_model_url}
fi

if [[ ! -f ${refiner_model_file} ]]; then
    wget -O ${refiner_model_file} ${refiner_model_url}
fi

if [[ ! -f ${sdxl_vae_file} ]]; then
    wget -O ${sdxl_vae_file} ${sdxl_vae_url}
fi

if [[ ! -f ${offset_lora_file} ]]; then
    wget -O ${offset_lora_file} ${offset_lora_url}
fi

if [[ ! -f ${siax_upscale_file} ]]; then
    wget -O ${siax_upscale_file} ${siax_upscale_url}
fi

if [[ ! -f ${ultrasharp_upscale_file} ]]; then
    wget -O ${ultrasharp_upscale_file} ${ultrasharp_upscale_url}
fi