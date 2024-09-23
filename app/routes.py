from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse, StreamingResponse
from starlette.responses import FileResponse
import json
import base64
import asyncio
from app.models import WebhookRequest
from app.utils import get_model, list_models
from app.tts import tts
from app.rvc import rvc
from app.payment import get_payment
from app.config import load_config

config = load_config()

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

    async def get_events():
        while True:
            event = await app.queue.get()
            yield f"event: Message\ndata: {event}\n\n"

    @app.get("/models")
    def api_list_models():
        models = list_models()
        return JSONResponse(content=models)
    
    @app.post("/receive")
    async def receive_webhook(request: WebhookRequest):
        try:
            payment = get_payment(request.payment_hash)

            if not payment['metadata']['text']:
                raise HTTPException(status_code=400, detail="No text provided")
            
            if int(payment['amount']) < config.MIN_SATOSHI_QNT:
                raise HTTPException(status_code=400, detail="Minimum payment not made")

            if payment['state'] != 'SETTLED':
                raise HTTPException(status_code=400, detail="Payment was not made")
            
            text = payment['metadata']['text'][:config.MAX_TEXT_LENGTH]
            amount = payment.get('amount', 'alguns')
            name = payment.get('metadata', {}).get('name', 'Anônimo')
            model = payment.get('metadata', {}).get('model', None)

            text = f"{name} enviou {amount} satoshis: {text}"

            audio_data = await generate(text=text, model_name=model)

            await app.queue.put(json.dumps({
                "text": text,
                "audio": audio_data.decode("utf-8"),
            }))

            return Response(status_code=200, content="ok")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    @app.get("/widget")
    def widget():
        return FileResponse('widget/index.html')

    @app.get("/events")
    def widget_events():
        return StreamingResponse(get_events(), media_type="text/event-stream")