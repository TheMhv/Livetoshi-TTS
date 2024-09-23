from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import setup_routes
from app.config import load_config

def create_app():
    app = FastAPI()
    
    config = load_config()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_routes(app)
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    config = load_config()
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)