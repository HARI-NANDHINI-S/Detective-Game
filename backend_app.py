import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import importlib.util
spec = importlib.util.spec_from_file_location("root_backend", os.path.join(root_dir, "backend_app.py"))
root_backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_backend)

app = root_backend.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
