def run(payload):
  if payload["name"]:
    name = payload["name"]
  else:
    name = "World"
  
  return f"Hello {name}!"