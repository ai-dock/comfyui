# Key is relative to $WORKSPACE/storage/

declare -A storage_map
storage_map["stable_diffusion/models/ckpt"]="/opt/ComfyUI/models/checkpoints"
storage_map["stable_diffusion/models/lora"]="/opt/ComfyUI/models/loras"
storage_map["stable_diffusion/models/controlnet"]="/opt/ComfyUI/models/controlnet"
storage_map["stable_diffusion/models/vae"]="/opt/ComfyUI/models/vae"
storage_map["stable_diffusion/models/esrgan"]="/opt/ComfyUI/models/upscale_models"

# Add more mappings for other repository directories as needed