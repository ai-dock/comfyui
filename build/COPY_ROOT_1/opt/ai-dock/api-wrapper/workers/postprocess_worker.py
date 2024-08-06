import asyncio
import aiobotocore.session
import aiofiles
import aiofiles.os
from config import config
from pathlib import Path

class PostprocessWorker:
    """
    Upload generated assets and fire webhook response
    """
    def __init__(self, worker_id, kwargs):
        self.worker_id = worker_id
        self.preprocess_queue = kwargs["preprocess_queue"]
        self.generation_queue = kwargs["generation_queue"]
        self.postprocess_queue = kwargs["postprocess_queue"]
        self.request_store = kwargs["request_store"]
        self.response_store = kwargs["response_store"]

    async def work(self):
        print ("PostprocessWorker: waiting for job")
        while True:
            # Get a task from the job queue
            request_id = await self.postprocess_queue.get()
            if request_id is None:
                # None is a signal that there are no more tasks
                break

            # Process the job
            print(f"PostprocessWorker {self.worker_id} processing job: {request_id}")
            try:
                request = await self.request_store.get(request_id)
                result = await self.response_store.get(request_id)
                
                await self.move_assets(request_id, result)
                await self.upload_assets(request_id, request.input.s3.get_config(), result)

                result.status = "success"
                result.message = "Process complete."
                
            except Exception as e:
                print(e)
                result.status = "failed"
                result.message = f"Postprocessing failed: {e}"
                await self.response_store.set(request_id, result)
            
            await self.response_store.set(request_id, result)

            # Mark the job as complete
            self.postprocess_queue.task_done()
            
        print(f"PostprocessWorker {self.worker_id} finished.")
    
    async def move_assets(self, request_id, result):
        custom_output_dir = f"{config.OUTPUT_DIR}{request_id}"
        await aiofiles.os.makedirs(custom_output_dir, exist_ok=True)

        for key, value in result.comfyui_response['outputs'].items():
            for inner_key, inner_value in value.items():
                if isinstance(inner_value, list):
                    for item in inner_value:
                        if item.get("type") == "output":
                            original_path = f"{config.OUTPUT_DIR}{item['subfolder']}/{item['filename']}"
                            new_path = f"{custom_output_dir}/{item['filename']}"

                            # Handle duplicated request where output file is not re-generated
                            if await aiofiles.os.path.islink(original_path):
                                real_path = await aiofiles.os.readlink(original_path)
                                async with aiofiles.open(real_path, 'rb') as src_file, aiofiles.open(new_path, 'wb') as dst_file:
                                    file_stat = await aiofiles.os.stat(real_path)
                                    await aiofiles.os.sendfile(dst_file.fileno(), src_file.fileno(), 0, file_stat.st_size)
                            else:
                                await aiofiles.os.rename(original_path, new_path)
                                await aiofiles.os.symlink(new_path, original_path)
                            key = f"{request_id}/{item['filename']}"
                            result.output.append({
                                "local_path": new_path
                            })

    async def upload_assets(self, request_id, s3_config, result):
        session = aiobotocore.session.get_session()
        async with session.create_client(
            's3',
            aws_access_key_id=s3_config["access_key_id"],
            aws_secret_access_key=s3_config["secret_access_key"],
            endpoint_url=s3_config["endpoint_url"],
            config=aiobotocore.config.AioConfig(
                connect_timeout=int(s3_config["connect_timeout"]),
                retries={"max_attempts": int(s3_config["connect_attempts"])}
            )
        ) as s3_client:
            tasks = []
            for obj in result.output:
                local_path = obj["local_path"]
                task = asyncio.create_task(self.upload_file_and_get_url(request_id, s3_client, s3_config["bucket_name"], local_path))
                tasks.append(task)
        
            # Run all tasks concurrently
            presigned_urls = await asyncio.gather(*tasks)
            
            # Append the presigned URLs to the respective objects
            for obj, url in zip(result.output, presigned_urls):
                obj["url"] = url

    async def upload_file_and_get_url(self, requst_id, s3_client, bucket_name, local_path):
        # Get the file name from the local path
        file_name = f"{requst_id}/{Path(local_path).name}"
        print (f"uploading {file_name}")

        try:
            # Upload the file
            with open(local_path, 'rb') as file:
                await s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=file)

            # Generate presigned URL
            presigned_url = await s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_name},
                ExpiresIn=604800  # URL expiration time in seconds
            )
            return presigned_url
        except Exception as e:
            print(f"Error uploading {local_path}: {e}")
            return None