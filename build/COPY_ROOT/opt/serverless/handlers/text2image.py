from handlers.basehandler import BaseHandler
import random
import time


"""
Handler classes are generally bound to a specific workflow file.
To modify values we have to be confident in the json structure.

One exception - RawWorkflow will send payload['workflow_json'] to the ComfyUI API after
downloading any URL's to the input directory and replacing the URL with a local path.
"""

class Text2Image(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/text2image.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
        

    def apply_modifiers(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.prompt["prompt"]["3"]["inputs"]["seed"] = self.get_value(
            "seed",
            random.randint(0,2**32))
        self.prompt["prompt"]["3"]["inputs"]["steps"] = self.get_value(
            "steps",
            20)
        self.prompt["prompt"]["3"]["inputs"]["sampler_name"] = self.get_value(
            "sampler_name",
            "euler")
        self.prompt["prompt"]["3"]["inputs"]["scheduler"] = self.get_value(
            "scheduler",
            "normal")
        self.prompt["prompt"]["4"]["inputs"]["ckpt_name"] = self.get_value(
            "ckpt_name",
            "v1-5-pruned-emaonly.ckpt")
        self.prompt["prompt"]["5"]["inputs"]["width"] = self.get_value(
            "width",
            512)
        self.prompt["prompt"]["5"]["inputs"]["height"] = self.get_value(
            "height",
            512)
        self.prompt["prompt"]["5"]["inputs"]["batch_size"] = self.get_value(
            "batch_size",
            1)
        self.prompt["prompt"]["6"]["inputs"]["text"] = self.get_value(
            "include_text",
            "")
        self.prompt["prompt"]["7"]["inputs"]["text"] = self.get_value(
            "exclude_text",
            "")

        
        
"""
Example Request Body:

{
    "input": {
        "handler": "Text2Image",
        "aws_access_key_id": "your-s3-access-key",
        "aws_secret_access_key": "your-s3-secret-access-key",
        "aws_endpoint_url": "https://my-endpoint.backblaze.com",
        "aws_bucket_name": "your-bucket",
        "webhook_url": "your-webhook-url",
        "webhook_extra_params": {},
        "steps": 20,
        "ckpt_name": "v1-5-pruned-emaonly.ckpt",
        "sampler_name": "euler",
        "scheduler": "normal",
        "include_text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
        "exclude_text": "text, watermark",
        "width": 512,
        "height": 512,
        "batch_size": 1
    }
}

"""
           
