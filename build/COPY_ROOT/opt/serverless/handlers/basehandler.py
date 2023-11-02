import json
import requests
import datetime
import time
import random
import sys
import os
from PIL import Image
import base64
import uuid

class BaseHandler:
    ENDPOINT_PROMPT="http://127.0.0.1:18188/prompt"
    ENDPOINT_QUEUE="http://127.0.0.1:18188/queue"
    ENDPOINT_HISTORY="http://127.0.0.1:18188/history"
    INPUT_DIR=f"{os.environ.get('WORKSPACE')}/ComfyUI/input/"
    OUTPUT_DIR=f"{os.environ.get('WORKSPACE')}/ComfyUI/output/"

    comfyui_job_id = None
    
    def __init__(self, payload, workflow_json = None):
          self.job_time_received = datetime.datetime.now()
          self.payload = payload
          self.workflow_json = workflow_json
          self.request_id = str(self.get_value(
            "request_id",
            uuid.uuid4()))
          self.set_prompt()
    
    def set_prompt(self):
        if self.workflow_json:
            with open(self.workflow_json, 'r') as f:
                self.prompt = {"prompt": json.load(f)}
        else:
            self.prompt = {"prompt": self.payload["workflow_json"]}
          
    def get_value(self, key, default = None):
        if key not in self.payload:
            return default
        return self.payload[key]
    
    def is_server_ready(self):
        try:
            req = requests.head(self.ENDPOINT_PROMPT)
            return True if req.status_code == 200 else False
        except:
            return False

        
    def queue_job(self, timeout = 30):
        self.job_time_queued = datetime.datetime.now()
        while ((datetime.datetime.now() - self.job_queued_time).seconds < timeout) and not self.is_server_ready():
            print(f"waiting for local server...")
            time.sleep(0.5)
        
        if not self.is_server_ready():
            raise requests.RequestException(f"Server not ready after timeout ({timeout}s)")
        
        print ("Posting job to local server...")
        data = json.dumps(self.prompt).encode('utf-8')
        response = requests.post(self.ENDPOINT_PROMPT, data=data).json()
        return response["prompt_id"]
    
    def get_job_status(self):
        history = requests.get(self.ENDPOINT_HISTORY).json()
        if self.comfyui_job_id in history:
            self.job_time_processed = datetime.datetime.now()
            return "complete"
        queue = requests.get(self.ENDPOINT_QUEUE).json()
        for job in queue["queue_running"]:
            if self.comfyui_job_id in job:
                return "running"
        for job in queue["queue_pending"]:
            if self.comfyui_job_id in job:
                return "pending"
        
        raise requests.RequestException("Failed to queue job")
    
    def image_to_base64(self, path):
        with open(path, "rb") as f:
            b64 = (base64.b64encode(f.read()))
        return b64
    
    def get_result(self, job_id):
        result = requests.get(self.ENDPOINT_HISTORY).json()[self.comfyui_job_id]

        prompt = result["prompt"]
        outputs = result["outputs"]

        self.result = {
            "images": [],
            "timings": {}
        }

        for item in outputs:
            if "images" in outputs[item]:
                for image in outputs[item]["images"]:
                    path = f"{self.OUTPUT_DIR}{image['subfolder']}/{image['filename']}"
                    
                    self.result["images"].append({
                        "local_path": path,
                        "base64": self.image_to_base64(path)
                    })
        
        self.job_time_completed = datetime.datetime.now()
        self.result["timings"] = {
            "job_time_received": self.job_time_received,
            "job_time_queued": self.job_time_queued,
            "job_time_processed": self.job_time_processed,
            "job_time_completed": self.job_time_completed,
            "job_time_total": (self.job_completed_time - self.job_received_time).seconds
        }

        return self.result
    
    def handle(self):
        self.comfyui_job_id = self.queue_job(30)
        
        status = None
        while status != "complete":
            status = self.get_job_status()
            if status != "complete":
                print (f"Waiting for {status} job to complete")
                time.sleep(0.5)

        return self.get_result(self.comfyui_job_id)