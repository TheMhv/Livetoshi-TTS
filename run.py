from rvc_python.infer import RVCInference
from dotenv import load_dotenv
from api import create_app
import uvicorn
import os

load_dotenv()

# Create and configure FastAPI app
app = create_app()

# Set up server options
host = str(os.getenv("SERVER_HOST"))
port = int(os.getenv("SERVER_PORT"))
print(f"Starting API server on {host}:{port}")

# Run the server
uvicorn.run(app, host=host, port=port)