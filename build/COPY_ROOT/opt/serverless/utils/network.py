from urllib.parse import urlparse
import requests
import os
import uuid

class Network:
    def __init__(self):
        pass

    @staticmethod
    def is_url(value):
        try:
            return bool(urlparse(value)[0])
        except:
            return False
    
    # todo - threads 
    @staticmethod
    def download_file(url, target_dir, request_id):
        try:
            os.makedirs(target_dir, exist_ok=True)
            response = requests.get(url, timeout=5)
            if response.status_code > 399:
                raise requests.RequestException(f"Unable to download {url}")
            if "content-disposition" in response.headers:
                content_disposition = response.headers["content-disposition"]
                filename = content_disposition.split("filename=")[1]
            else:
                filename = url.split("/")[-1]
            
            filepath = f"{target_dir}/{request_id}-{uuid.uuid4()}-{filename}"
            with open(filepath, mode="wb") as file:
                file.write(response.content)
        except:
            raise

        print(f"Downloaded {url} to {filepath}")
        return filepath
    
    @staticmethod
    def invoke_webhook(url, data):
        try:
            response = requests.post(url, json=data)
            print(f"Invoke webhook {url} with data {data} - status {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request: {e}")
            return None
