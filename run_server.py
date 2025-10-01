import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("run_server:app", host="127.0.0.1", port=8001, reload=True)