import asyncio
from config import config
from fastapi import FastAPI, Response, Body
from typing import Annotated, List
from aiocache import Cache, SimpleMemoryCache
from requestmodels.models import Payload
from responses.result import Result
from workers.preprocess_worker import PreprocessWorker
from workers.generation_worker import GenerationWorker
from workers.postprocess_worker import PostprocessWorker
import uuid

app = FastAPI(root_path="/ai-dock/api")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())

# Simple memory based caching by default
# This worker is not expected to handle disaster recovery
# See ai-dock/comfyui-load-balancer for advanced usage (TODO)
if config.CACHE_TYPE == "redis":
    request_store = Cache(Cache.REDIS, namespace="request_store")
    response_store = Cache(Cache.REDIS, namespace="response_store")
else:
    request_store = SimpleMemoryCache(namespace="request_store")
    response_store = SimpleMemoryCache(namespace="response_store")

    # Check payload for URLs and download as required
    preprocess_queue = asyncio.Queue()    
    # Generate outputs with ComfyUI
    generation_queue = asyncio.Queue()
    # Upload outputs, webhook, cleanup
    postprocess_queue = asyncio.Queue()
    

async def main():
    worker_config = {
        "preprocess_queue": preprocess_queue,
        "generation_queue": generation_queue,
        "postprocess_queue": postprocess_queue,
        "request_store": request_store,
        "response_store": response_store,
    }

    preprocess_workers = [PreprocessWorker(i, worker_config) for i in range(1, 4)]
    preprocess_tasks = [asyncio.create_task(worker.work()) for worker in preprocess_workers]

    # One initially - May extend this to several
    generation_workers = [GenerationWorker(i, worker_config) for i in range(1, 2)]
    generation_tasks = [asyncio.create_task(worker.work()) for worker in generation_workers]

    postprocess_workers = [PostprocessWorker(i, worker_config) for i in range(1, 4)]
    postprocess_tasks = [asyncio.create_task(worker.work()) for worker in postprocess_workers]

    # Wait indefinitely
    await asyncio.gather(*preprocess_tasks, *generation_tasks, *postprocess_tasks)


  
@app.post('/payload', response_model=Result, status_code=202)
async def payload(
    payload: Annotated[
        Payload,
        Body(
            openapi_examples=Payload.get_openapi_examples()
        ),
    ],
):

    if not payload.input.request_id:
        payload.input.request_id = str(uuid.uuid4())
    request_id = payload.input.request_id
    
    result_pending = Result(id=request_id)

    # Immediately store request for crash recovery (redis)
    await request_store.set(request_id, payload)
    await response_store.set(request_id, result_pending)
    await preprocess_queue.put(request_id)
    
    return result_pending


@app.get('/result/{request_id}', response_model=Result, status_code=200)
async def result(request_id: str, response: Response):
    result = await response_store.get(request_id)
    if not result:
        result = Result(id=request_id, status="failed", message="Request ID not found")
        response.status_code = 404
    
    return result

@app.get('/queue-info', response_model=List[str])
async def queue_info():
    return list(request_queue.queue)

        