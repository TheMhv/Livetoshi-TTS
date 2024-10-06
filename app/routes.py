from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
import json
import base64
import asyncio
import os
from typing import Dict
from app.models import InvoiceMetadata, WebhookRequest
from app.utils import get_model, list_models
from app.tts import tts
from app.rvc import rvc
from app.config import load_config
from app.listener import listener

config = load_config()

pending_payments: Dict[str, asyncio.Event] = {}

async def generate(text: str, model_name: str | None):
    model = get_model(model_name) if model_name else None
    tts_file = await tts(model=model, text=text)

    if not model:
        with open(tts_file.name, "rb") as f:
            audio_data = base64.b64encode(f.read())
        
        os.unlink(tts_file.name)
        return audio_data

    return await rvc(model=model, audio_path=tts_file.name)

def setup_routes(app: FastAPI):
    app.queue = asyncio.Queue()
    app.mount("/widget", StaticFiles(directory="widget", html=True), name="widget")

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(listener(app))

    async def get_events():
        while True:
            event = await app.queue.get()
            yield f"event: Message\ndata: {event}\n\n"

    @app.get("/events")
    def widget_events():
        return StreamingResponse(get_events(), media_type="text/event-stream")