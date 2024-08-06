from modifiers.basemodifier import BaseModifier
import random
import time
import json


"""
Handler classes are generally bound to a specific workflow file.
To modify values we have to be confident in the json structure.

One exception - RawWorkflow will send payload['workflow_json'] to the ComfyUI API after
downloading any URL's to the input directory and replacing the URL with a local path.
"""

class Text2Image(BaseModifier):
    
    WORKFLOW_JSON = "workflows/image2image.json"
    
    def __init__(self, modificafions={}):
        super().__init__()
        self.modificafions = modificafions

    async def apply_modifications(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.workflow["3"]["inputs"]["seed"] = await self.modify_workflow_value(
            "seed",
            random.randint(0,2**32))
        self.workflow["3"]["inputs"]["steps"] = await self.modify_workflow_value(
            "steps",
            20)
        self.workflow["3"]["inputs"]["sampler_name"] = await self.modify_workflow_value(
            "sampler_name",
            "dpmpp_2m")
        self.workflow["3"]["inputs"]["scheduler"] = await self.modify_workflow_value(
            "scheduler",
            "normal")
        self.workflow["3"]["inputs"]["denoise"] = await self.modify_workflow_value(
            "denoise",
            0.8700000000000001)
        self.workflow["6"]["inputs"]["text"] = await self.modify_workflow_value(
            "include_text",
            "")
        self.workflow["7"]["inputs"]["text"] = await self.modify_workflow_value(
            "exclude_text",
            "")
        self.workflow["10"]["inputs"]["image"] = await self.modify_workflow_value(
            "input_image"
            )
        self.workflow["14"]["inputs"]["ckpt_name"] = await self.modify_workflow_value(
            "ckpt_name",
            "v1-5-pruned-emaonly.ckpt")
        await super().apply_modifications()

        
"""
Example Request Body:

{
    "input": {
        "modifier": "Image2Image",
        "aws_access_key_id": "your-s3-access-key",
        "aws_secret_access_key": "your-s3-secret-access-key",
        "aws_endpoint_url": "https://my-endpoint.backblaze.com",
        "aws_bucket_name": "your-bucket",
        "webhook_url": "your-webhook-url",
        "webhook_extra_params": {},
        "ckpt_name": "v1-5-pruned-emaonly.ckpt",
        "include_text": "photograph of a victorian woman, arms outstretched with angel wings. cloudy sky, meadow grass",
        "exclude_text": "watermark, text",
        "denoise": 0.87,
        "input_image": "https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/input/example.png"
    }
}

"""
           
