import datetime
import aiogoogle.auth.creds
import aiogoogle.client
import asyncio
import itertools
import aiobotocore.session
import aiofiles
import aiofiles.os
from google.oauth2 import service_account
from google.cloud.storage import _signing as signing
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

                named_upload_tasks = []
                if (s3_config := request.input.s3.get_config()):
                    async def upload_s3_assets():
                        return ("s3", await self.upload_s3_assets(request_id, s3_config, result))
                    named_upload_tasks.append(
                        asyncio.create_task(upload_s3_assets()))
                if (gcp_config := request.input.gcp.get_config()):
                    async def upload_gcp_assets():
                        return ("gcp", await self.upload_gcp_assets(request_id, gcp_config, result))
                    named_upload_tasks.append(
                        asyncio.create_task(upload_gcp_assets()))
                if named_upload_tasks:
                    named_presigned_urls = dict(await asyncio.gather(*named_upload_tasks))
                    presigned_urls = itertools.zip_longest(
                        named_presigned_urls.get("s3", []),
                        named_presigned_urls.get("gcp", []),
                        fillvalue=None)
                    for obj, (s3_url, gcp_url) in zip(result.output, presigned_urls):
                        if s3_url:
                            # Keeping for backward compatibility
                            obj["url"] = s3_url
                            obj["s3_url"] = s3_url
                        if gcp_url:
                            obj["gcp_url"] = gcp_url

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

    async def upload_s3_assets(self, request_id, s3_config, result):
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
            return await asyncio.gather(*tasks)

    async def upload_file_and_get_url(self, request_id, s3_client, bucket_name, local_path):
        # Get the file name from the local path
        file_name = f"{request_id}/{Path(local_path).name}"
        print(f"uploading to s3 {file_name}")

        try:
            # Upload the file
            with open(local_path, 'rb') as file:
                await s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=file)

            # Generate presigned URL
            presigned_url = await s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_name},
                ExpiresIn=int(datetime.timedelta(days=7).total_seconds()),
            )
            return presigned_url
        except Exception as e:
            print(f"Error uploading to s3 {local_path}: {e}")
            return None

    async def upload_gcp_assets(self, request_id, gcp_config, result):
        creds = aiogoogle.auth.creds.ServiceAccountCreds(
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
            **gcp_config["credentials"],
        )
        google_credentials = service_account.Credentials.from_service_account_info(
            gcp_config["credentials"])
        aiog_client = aiogoogle.client.Aiogoogle(service_account_creds=creds)
        async with aiog_client:
            # Not needed as we are using provided service account creds. Uncomment if using discovery.
            # await aiog_client.service_account_manager.detect_default_creds_source()
            storage = await aiog_client.discover("storage", "v1")
            tasks = []
            for obj in result.output:
                local_path = obj["local_path"]
                task = asyncio.create_task(self.upload_file_to_gcp_and_get_url(
                    request_id, aiog_client, storage, gcp_config["bucket_name"], local_path, google_credentials))
                tasks.append(task)

            # Run all tasks concurrently
            return await asyncio.gather(*tasks)

    async def upload_file_to_gcp_and_get_url(self, request_id, aiog_client, storage, bucket_name, local_path, google_credentials):
        destination_path = f"{request_id}/{Path(local_path).name}"
        print(f"uploading to gcp {destination_path}")

        try:
            await aiog_client.as_service_account(storage.objects.insert(
                bucket=bucket_name,
                name=destination_path,
                upload_file=local_path,
            ), full_res=True)
            return signing.generate_signed_url_v4(
                google_credentials,
                f"/{bucket_name}/{destination_path}",
                expiration=datetime.timedelta(days=7),
                method="GET",
            )
        except Exception as e:
            print(f"Error uploading to gcp {local_path}: {e}")
            return None
