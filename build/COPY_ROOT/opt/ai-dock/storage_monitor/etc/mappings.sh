# Key is relative to $WORKSPACE/storage/

declare -A storage_map
storage_map["stable_diffusion/models/ckpt"]="/opt/ComfyUI/models/checkpoints"
storage_map["stable_diffusion/models/controlnet"]="/opt/ComfyUI/models/controlnet"
storage_map["stable_diffusion/models/diffusers"]="/opt/ComfyUI/models/diffusers"
storage_map["stable_diffusion/models/embeddings"]="/opt/ComfyUI/models/embeddings"
storage_map["stable_diffusion/models/esrgan"]="/opt/ComfyUI/models/upscale_models"
storage_map["stable_diffusion/models/gligen"]="/opt/ComfyUI/models/gligen"
storage_map["stable_diffusion/models/hypernetworks"]="/opt/ComfyUI/models/hypernetworks"
storage_map["stable_diffusion/models/lora"]="/opt/ComfyUI/models/loras"
storage_map["stable_diffusion/models/style_models"]="/opt/ComfyUI/models/style_models"
storage_map["stable_diffusion/models/unet"]="/opt/ComfyUI/models/unet"
storage_map["stable_diffusion/models/vae"]="/opt/ComfyUI/models/vae"
storage_map["stable_diffusion/models/vae_approx"]="/opt/ComfyUI/models/upscale_models"

# Add more mappings for other repository directories as needed