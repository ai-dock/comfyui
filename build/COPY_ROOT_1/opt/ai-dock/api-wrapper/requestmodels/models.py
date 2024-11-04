from typing import Dict
from pydantic import BaseModel, Field
import os
import json

if os.environ.get("GCP_CREDENTIALS"):
    with open(os.environ["GCP_CREDENTIALS"]) as f:
        _GCP_CREDENTIALS = json.load(f)
else:
    _GCP_CREDENTIALS = {}

class S3Config(BaseModel):
    access_key_id: str = Field(default=os.environ.get("S3_ACCESS_KEY_ID", ""))
    secret_access_key: str = Field(
        default=os.environ.get("S3_SECRET_ACCESS_KEY", ""))
    endpoint_url: str = Field(default=os.environ.get("S3_ENDPOINT_URL", ""))
    bucket_name: str = Field(default=os.environ.get("S3_BUCKET_NAME", ""))
    connect_timeout: int = Field(default=5)
    connect_attempts: int = Field(default=1)
    
    def get_config(self):
        config = {"access_key_id": self.access_key_id,
                  "secret_access_key": self.secret_access_key,
                  "endpoint_url": self.endpoint_url,
                  "bucket_name": self.bucket_name,
                  "connect_timeout": self.connect_timeout,
                  "connect_attempts": self.connect_attempts}
        set_values = sum(1 for v in config.values() if v)
        return config if set_values > 2 else {}

class GcpConfig(BaseModel):
    credentials: Dict = Field(default_factory=_GCP_CREDENTIALS.copy)
    project_id: str = Field(default=os.environ.get("GCP_PROJECT_ID", ""))
    bucket_name: str = Field(default=os.environ.get("GCP_BUCKET_NAME", ""))
    
    def get_config(self):
        config = {"credentials": self.credentials,
                  "project_id": self.project_id,
                  "bucket_name": self.bucket_name}
        set_values = sum(1 for v in config.values() if v)
        return config if set_values > 0 else {}

class WebHook(BaseModel):
    url: str = Field(default="")
    extra_params: Dict = Field(default_factory=dict)
    
    def has_valid_url(self):
        return network.is_url(self.url)

class Input(BaseModel):
    request_id: str = Field(default="")
    modifier: str = Field(default="")
    modifications: Dict = Field(default_factory=dict)
    workflow_json: Dict = Field(default_factory=dict)
    s3: S3Config = Field(default_factory=S3Config)
    gcp: GcpConfig = Field(default_factory=GcpConfig)
    webhook: WebHook = Field(default_factory=WebHook)
    
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

        