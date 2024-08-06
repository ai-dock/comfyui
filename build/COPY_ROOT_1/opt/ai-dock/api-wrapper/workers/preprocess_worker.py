import importlib
from modifiers.basemodifier import BaseModifier

class PreprocessWorker:
    """
    Check for URL's in the payload and download the assets as required
    """
    def __init__(self, worker_id, kwargs):
        self.worker_id = worker_id
        self.preprocess_queue = kwargs["preprocess_queue"]
        self.generation_queue = kwargs["generation_queue"]
        self.postprocess_queue = kwargs["postprocess_queue"]
        self.request_store = kwargs["request_store"]
        self.response_store = kwargs["response_store"]

    async def work(self):
        print ("PreprocessWorker: waiting for job")
        while True:
            # Get a task from the job queue
            request_id = await self.preprocess_queue.get()
            if request_id is None:
                # None is a signal that there are no more tasks
                break

            # Process the job
            print(f"PreprocessWorker {self.worker_id} processing job: {request_id}")
            try:
                request = await self.request_store.get(request_id)
                result = await self.response_store.get(request_id)
                modifier = await self.get_workflow_modifier(request.input.modifier, request.input.modifications)
                await modifier.load_workflow(request.input.workflow_json)
                request.input.workflow_json = await modifier.get_modified_workflow()
                await self.request_store.set(request_id, request)
            except Exception as e:
                result.status = "failed"
                result.message = f"Workflow modifier failed: {e}"
                await self.response_store.set(request_id, result)
                # Send job straight to postprocess for fail result
                await self.postprocess_queue.put(request_id)
            
            result.message = "Preprocessing complete. Queued for generation."
            await self.response_store.set(request_id, result)
            # Send for ComfyUI generation
            await self.generation_queue.put(request_id)
            # Mark the job as complete
            self.preprocess_queue.task_done()
            
        print(f"PreprocessWorker {self.worker_id} finished.")
        return

    async def get_workflow_modifier(self, modifier_name: str, modifiers: dict) -> BaseModifier:
        try:
            if modifier_name:
                module = importlib.import_module(f'modifiers.{modifier_name.lower()}')
                modifier_class = getattr(module, modifier_name)
            else:
                modifier_class = BaseModifier
            return modifier_class(modifiers)
        except:
            raise
    
    