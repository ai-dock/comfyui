import os
COMFYUI_API_BASE="http://127.0.0.1:18188"
COMFYUI_API_PROMPT=f"{COMFYUI_API_BASE}/prompt"
COMFYUI_API_QUEUE=f"{COMFYUI_API_BASE}/queue"
COMFYUI_API_HISTORY=f"{COMFYUI_API_BASE}/history"

if os.getenv("API_CACHE", 'memory').lower() == "redis":
    CACHE_TYPE="redis"
else:
    CACHE_TYPE = "memory"

INPUT_DIR=f"/opt/ComfyUI/input/"
OUTPUT_DIR=f"/opt/ComfyUI/output/"
