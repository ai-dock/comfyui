import asyncio
import os
import json
import hashlib
import aiofiles
import aiohttp
import magic
import mimetypes
from urllib.parse import urlparse
from config import config
from pathlib import Path

class BaseModifier:
    WORKFLOW_JSON = ""
  
    def __init__(self, modifications={}):
        self.modifications = modifications
        self.input_dir = config.INPUT_DIR
    
    async def load_workflow(self, workflow={}):
        if workflow and not self.WORKFLOW_JSON:
            self.workflow = workflow
        else:
            try:
                async with aiofiles.open(self.WORKFLOW_JSON, 'r') as f:
                    file_content = await f.read()
                    self.workflow = json.loads(file_content)
            except Exception as e:
                raise Exception(f"Could not load workflow ({e})")
        
    async def modify_workflow_value(self, key, default = None):
        """
        Modify a workflow value after loading the json.
        """
        if key not in self.modifications and default == None:
            raise IndexError(f"{key} required but not set")
        elif key not in self.modifications:
            return default
        else:
            return self.modifications[key]

    async def replace_workflow_urls(self, data):
        """
        Find all URL strings in the prompt and replace the URL string with a filepath
        """
        if isinstance(data, dict):
            for key, value in data.items():
                data[key] = await self.replace_workflow_urls(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                data[i] = await self.replace_workflow_urls(item)
        elif isinstance(data, str) and self.is_url(data):
            data = await self.get_url_content(data)
        return data
            
    async def get_url_content(self, url):
        """
        Download from URL to ComfyUI input directory as hash.ext to avoid downloading the resource
        multiple times
        """
        filename_without_extension = self.get_url_hash(url)
        existing_file = await self.find_input_file(
            self.input_dir,
            filename_without_extension
        )
        if existing_file:
            return os.path.basename(existing_file)
        else:
            file_name = os.path.basename(await self.download_file(
                url,
                self.input_dir
            ))
            return file_name
    
    def is_url(self, value):
        try:
            return bool(urlparse(value)[0])
        except:
            return False
    
    def get_url_hash(self, url):
        return hashlib.md5((f'{url}').encode()).hexdigest()
    
    async def download_file(self, url, target_dir):
        try:
            file_name_hash = self.get_url_hash(url)
            os.makedirs(target_dir, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status > 399:
                        raise aiohttp.ClientResponseError(status=response.status, message=f"Unable to download {url}")
                    
                    filepath_hash = f"{target_dir}/{file_name_hash}"
                    async with aiofiles.open(filepath_hash, mode="wb") as file:
                        await file.write(await response.read())
                    
                    file_extension = await self.get_file_extension(filepath_hash)
                    filepath = f"{filepath_hash}{file_extension}"
                    os.replace(filepath_hash, filepath)
                    
        except Exception as e:
            raise e

        print(f"Downloaded {url} to {filepath}")
        return filepath
    
    async def find_input_file(self, directory, filename_without_extension):
        try:
            directory_path = Path(directory)
            loop = asyncio.get_running_loop()
            files = await loop.run_in_executor(None, self.list_files_in_directory, directory_path, filename_without_extension)
            if files:
                return files[0]
        except Exception as e:
            print(f"Error finding input file: {e}")
        return None
    
    def list_files_in_directory(self, directory_path, filename_without_extension):
        files = []
        for file in directory_path.glob(f"{filename_without_extension}*"):
            if file.is_file():
                files.append(file)
        return files
            
    async def get_file_extension(self, filepath):
        try:
            mime_str = magic.from_file(filepath, mime=True)
            extension = mimetypes.guess_extension(mime_str) or ".jpg"
            return extension
        except Exception as e:
            return ".jpg"  # Fallback to a default extension
    
          
    async def apply_modifications(self):
        await self.replace_workflow_urls(self.workflow)
            
    async def get_modified_workflow(self):
        await self.apply_modifications()
        return self.workflow