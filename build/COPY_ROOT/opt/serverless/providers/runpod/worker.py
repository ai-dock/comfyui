import sys
sys.path.append('/opt/serverless')
from pydoc import locate
import handlers
import runpod

def get_handler(payload):
    try:
        c_name = payload["handler"]
        m_name = c_name.lower()
        handler_class = locate(f"handlers.{m_name}.{c_name}")
        handler = handler_class(payload)
    except:
        raise
        raise IndexError(f"Handler ({c_name}) not found")
        
    return handler
  
'''
Handler to be specified in input.handler
'''
def worker(event):
    result = {}
    try:
        payload = event["input"]
        payload["request_id"] = event["id"]
        handler = get_handler(payload)
        result = handler.handle()
    except Exception as e:
        result = {}
        result["error"] = str(e)
    
    return result

runpod.serverless.start({
    "handler": worker
})