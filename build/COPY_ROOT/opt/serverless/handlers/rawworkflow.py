from handlers.basehandler import BaseHandler
import random


"""
Handler classes are generally bound to a specific workflow file.
To modify values we have to be confident in the json structure.

One exception - RawWorkflow will send payload['workflow_json'] to the ComfyUI API - TODO
"""

class RawWorkflow(BaseHandler):
    
    WORKFLOW_JSON = None
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
        

    def apply_modifiers(self):
        # TODO - Parse the workflow for image URLs, download and update the prompt 
        pass

        
        
"""
Example Request Body:

{
    "input": {
        "handler": "RawWorkflow",
        "aws_bucket_name": "ai-dock",
        "workflow_json": {
            "3": {
            "inputs": {
                "seed": 12345,
                "steps": 20,
                "cfg": 8,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": [
                "4",
                0
                ],
                "positive": [
                "6",
                0
                ],
                "negative": [
                "7",
                0
                ],
                "latent_image": [
                "5",
                0
                ]
            },
            "class_type": "KSampler"
            },
            "4": {
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.ckpt"
            },
            "class_type": "CheckpointLoaderSimple"
            },
            "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
            },
            "6": {
            "inputs": {
                "text": "a penguin chasing a polar bear",
                "clip": [
                "4",
                1
                ]
            },
            "class_type": "CLIPTextEncode"
            },
            "7": {
            "inputs": {
                "text": "text, watermark",
                "clip": [
                "4",
                1
                ]
            },
            "class_type": "CLIPTextEncode"
            },
            "8": {
            "inputs": {
                "samples": [
                "3",
                0
                ],
                "vae": [
                "4",
                2
                ]
            },
            "class_type": "VAEDecode"
            },
            "9": {
            "inputs": {
                "filename_prefix": "image",
                "images": [
                "8",
                0
                ]
            },
            "class_type": "SaveImage"
            }
        }
    }
}

"""
           
