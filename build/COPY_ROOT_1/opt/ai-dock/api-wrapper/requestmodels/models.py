from typing import List, Union, Dict, Annotated
from pydantic import BaseModel, Field
import os
import json

class S3Config(BaseModel):
    access_key_id: str = Field(default="")
    secret_access_key: str = Field(default="")
    endpoint_url: str = Field(default="")
    bucket_name: str = Field(default="")
    connect_timeout: int = Field(default=5)
    connect_attempts: int = Field(default=1)
    
    @staticmethod
    def get_defaults():
        return {
            "access_key_id": "",
            "secret_access_key": "",
            "endpoint_url": "",
            "bucket_name": "",
            "connect_timeout": "5",
            "connect_attempts": "1"
        }
    
    def get_config(self):
        return {
            "access_key_id": getattr(self, "access_key_id", os.environ.get("S3_ACCESS_KEY_ID", "")),
            "secret_access_key": getattr(self, "secret_access_key", os.environ.get("S3_SECRET_ACCESS_KEY", "")),
            "endpoint_url": getattr(self, "endpoint_url", os.environ.get("S3_ENDPOINT_URL", "")),
            "bucket_name": getattr(self, "bucket_name", os.environ.get("S3_BUCKET_NAME", "")),
            "connect_timeout": "5",
            "connect_attempts": "1"
        }

class WebHook(BaseModel):
    url: str = Field(default="")
    extra_params: Dict = Field(default={})
    
    @staticmethod
    def get_defaults():
        return {
            "url": "",
            "extra_params": {}
        }
    
    def has_valid_url(self):
        return network.is_url(self.url)

class Input(BaseModel):
    request_id: str = Field(default="")
    modifier: str = Field(default="")
    modifications: Dict = Field(default={})
    workflow_json: Dict = Field(default={})
    s3: S3Config = Field(default=S3Config.get_defaults())
    webhook: WebHook = Field(default=WebHook.get_defaults())
    
class Payload(BaseModel):
    input: Input
    
    @staticmethod
    def get_openapi_examples():
        directory = './payloads'
        result = {}
    
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = json.load(file)
                
                # Remove the file extension and convert to natural language
                key = Payload.snake_to_natural(os.path.splitext(filename)[0])
                
                # Add the content to the result dictionary
                result[key] = {"value": file_content}
        
        return result
    
    @staticmethod
    def snake_to_natural(snake_str):
        # Convert snake_case to Natural Language
        return ' '.join(word.capitalize() for word in snake_str.split('_'))

        