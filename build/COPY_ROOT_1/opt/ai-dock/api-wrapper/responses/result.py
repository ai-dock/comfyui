from pydantic import BaseModel, Field
from typing import Dict

class Result(BaseModel):
    id: str
    message: str = Field(default='Request accepted')
    status: str = Field(default='pending')
    comfyui_response: Dict = Field(default={})
    output: list = Field(default=[])
    timings: Dict = Field(default={})

