import json
import requests
import datetime
import time
import os
import base64
import uuid
from utils.s3utils import s3utils
from utils.network import Network

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
          self.s3utils = s3utils(self.get_s3_settings())
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
        if key not in self.payload and default == None:
            raise IndexError(f"{key} required but not set")
        elif key not in self.payload:
            return default
        elif Network.is_url(self.payload[key]):
            return os.path.basename(Network.download_file(
                self.payload[key], 
                self.get_input_dir(), 
                self.request_id
                    )
                )
        else:
            return self.payload[key]
    
    def get_input_dir(self):
        return f"{self.INPUT_DIR}{self.request_id}/"
    
    def get_output_dir(self):
        return f"{self.OUTPUT_DIR}"

    def is_server_ready(self):
        try:
            req = requests.head(self.ENDPOINT_PROMPT)
            return True if req.status_code == 200 else False
        except:
            return False

    def queue_job(self, timeout = 30):
        try:
            self.job_time_queued = datetime.datetime.now()
            while ((datetime.datetime.now() - self.job_time_queued).seconds < timeout) and not self.is_server_ready():
                print(f"waiting for local server...")
                time.sleep(0.5)
            
            if not self.is_server_ready():
                raise requests.RequestException(f"Server not ready after timeout ({timeout}s)")
            
            print ("Posting job to local server...")
            data = json.dumps(self.prompt).encode('utf-8')
            response = requests.post(self.ENDPOINT_PROMPT, data=data).json()
            if "prompt_id" in response:
                return response["prompt_id"]
            elif "node_errors" in response:
                raise requests.RequestException(response["node_errors"])
            elif "error" in response:
                raise requests.RequestException(response["error"])
        except requests.RequestException:
            raise
        except:
            raise requests.RequestException("Failed to queue prompt")
    
    def get_job_status(self):
        try:
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
        except:
            raise requests.RequestException("Failed to queue job")
    
    def image_to_base64(self, path):
        with open(path, "rb") as f:
            b64 = (base64.b64encode(f.read()))
        return "data:image/png;charset=utf-8;base64, " + b64
    
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
                    key = f"{image['subfolder']}/{image['filename']}"
                    self.result["images"].append({
                        "local_path": path,
                        #"base64": self.image_to_base64(path),
                        # make this work first, then threads
                        "url": self.s3utils.file_upload(path, key)
                    })
        
        self.job_time_completed = datetime.datetime.now()
        self.result["timings"] = {
            "job_time_received": self.job_time_received,
            "job_time_queued": self.job_time_queued,
            "job_time_processed": self.job_time_processed,
            "job_time_completed": self.job_time_completed,
            "job_time_total": (self.job_time_completed - self.job_time_received.seconds
        }

        return self.result
    
    def get_s3_settings(self):
        settings = {}
        settings["aws_access_key_id"] = self.get_value("aws_access_key_id", os.environ.get("AWS_ACCESS_KEY_ID"))
        settings["aws_secret_access_key"] = self.get_value("aws_secret_access_key", os.environ.get("AWS_SECRET_ACCESS_KEY"))
        settings["aws_endpoint_url"] = self.get_value("aws_endpoint_url", os.environ.get("AWS_ENDPOINT_URL"))
        settings["aws_bucket_name"] = self.get_value("aws_bucket_name", os.environ.get("AWS_BUCKET_NAME"))
        return settings
    
    def handle(self):
        self.comfyui_job_id = self.queue_job(30)
        
        status = None
        while status != "complete":
            status = self.get_job_status()
            if status != "complete":
                print (f"Waiting for {status} job to complete")
                time.sleep(0.5)

        return self.get_result(self.comfyui_job_id)