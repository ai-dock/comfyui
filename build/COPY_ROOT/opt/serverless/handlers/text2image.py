from handlers.basehandler import BaseHandler
import random


"""
Handler classes are generally bound to a specific workflow file.
To modify values we have to be confident in the json structure.

One exception - RawWorkflow will send payload['workflow_json'] to the ComfyUI API - TODO
"""

class Text2Image(BaseHandler):
    
    WORKFLOW_JSON = "/opt/serverless/workflows/text2image.json"
    
    def __init__(self, payload):
        super().__init__(payload, self.WORKFLOW_JSON)
        self.apply_modifiers()
        

    def apply_modifiers(self):
        self.prompt["prompt"]["3"]["inputs"]["seed"] = self.get_value(
            "seed",
            random.randint(0,2**32))
        self.prompt["prompt"]["4"]["inputs"]["ckpt_name"] = self.get_value(
            "ckpt_name",
            "v1-5-pruned-emaonly.ckpt")
        self.prompt["prompt"]["6"]["inputs"]["text"] = self.get_value(
            "include_text",
            "")
        self.prompt["prompt"]["7"]["inputs"]["text"] = self.get_value(
            "exclude_text",
            "")
        self.prompt["prompt"]["9"]["inputs"]["filename_prefix"] = f"{self.request_id}/image"

        
        
           
           
