import asyncio
import aiohttp
import json
from config import config

class GenerationWorker:
    """
    Send payload to ComfyUI and await completion
    """
    def __init__(self, worker_id, kwargs):
        self.worker_id = worker_id
        self.preprocess_queue = kwargs["preprocess_queue"]
        self.generation_queue = kwargs["generation_queue"]
        self.postprocess_queue = kwargs["postprocess_queue"]
        self.request_store = kwargs["request_store"]
        self.response_store = kwargs["response_store"]

    async def work(self):
        print ("GenerationWorker: waiting for job")
        while True:
            # Get a task from the job queue
            request_id = await self.generation_queue.get()
            if request_id is None:
                # None is a signal that there are no more tasks
                break

            # Process the job
            print(f"GenerationWorker {self.worker_id} processing job: {request_id}")
            try:
                request = await self.request_store.get(request_id)
                result = await self.response_store.get(request_id)
                comfyui_job_id = await self.post_workflow(request)

                # TODO: Add check to ensure job still running (websocket)
                while True:
                    complete = await self.is_workflow_complete(comfyui_job_id)
                    if not complete:
                        print("waiting for job")
                        await asyncio.sleep(1)
                    else:
                        print("job done")
                        break

                comfyui_response = await self.get_result(comfyui_job_id)
                
            except Exception as e:
                result.status = "failed"
                result.message = f"Generation failed: {e}"
                await self.response_store.set(request_id, result)
                # Send job straight to postprocess for fail result
                await self.postprocess_queue.put(request_id)
            
            result.message = "Generation complete. Queued for upload."
            result.comfyui_response = comfyui_response
            
            await self.response_store.set(request_id, result)
            # Send for ComfyUI generation
            await self.postprocess_queue.put(request_id)
            
            # Mark the job as complete
            self.generation_queue.task_done()

        print(f"PreprocessWorker {self.worker_id} finished.")
        return

    async def post_workflow(self, request):
        data = json.dumps(
          {
            "prompt": request.input.workflow_json,
            "client_id": request.input.request_id
          }).encode('utf-8')
 
        async with aiohttp.ClientSession() as session:
            try:
                print("Posting job to local server...")
                async with session.post(config.COMFYUI_API_PROMPT, data=data) as response:
                    response_data = await response.json()
                    if "prompt_id" in response_data:
                        return response_data["prompt_id"]
                    elif "node_errors" in response_data:
                        raise aiohttp.ClientError(response_data["node_errors"])
                    elif "error" in response_data:
                        raise aiohttp.ClientError(response_data["error"])
            except Exception as e:
                raise aiohttp.ClientError(f"Failed to queue prompt: {e}")
        
    async def is_workflow_complete(self, comfyui_job_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config.COMFYUI_API_HISTORY) as response:
                    history = await response.json()
                    if comfyui_job_id in history:
                        return True
        except Exception as e:
            raise e

    async def get_result(self, comfyui_job_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(config.COMFYUI_API_HISTORY) as response:
                history = await response.json()
                return history[comfyui_job_id]