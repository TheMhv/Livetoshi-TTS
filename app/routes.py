from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse, StreamingResponse
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
from app.payment import get_payment, create_payment
from app.config import load_config

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

    async def get_events():
        while True:
            event = await app.queue.get()
            yield f"event: Message\ndata: {event}\n\n"

    @app.post("/create_invoice")
    async def create_invoice(amount: int, metadata: InvoiceMetadata):
        try:
            if amount < config.MIN_SATOSHI_QNT:
                raise HTTPException(status_code=400, detail=f"Minimum amount is {config.MIN_SATOSHI_QNT} satoshis")
            
            invoice = create_payment(amount, metadata.dict())
            payment_hash = invoice['payment_hash']
            qr_code = invoice['qr_code_svg'] or invoice['qr_code_svg']
            
            # Create an event for this payment
            pending_payments[payment_hash] = asyncio.Event()
            
            return StreamingResponse(payment_stream(payment_hash, qr_code), media_type="text/event-stream")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create invoice: {str(e)}")

    async def payment_stream(payment_hash: str, qr_code: str):
        try:
            yield f"data: {json.dumps({'qr_code': qr_code})}\n\n"

            # Wait for the payment to be settled
            wait_task = asyncio.create_task(wait_for_payment(payment_hash))
            
            # Wait for the payment to settle or timeout after 5 minutes
            await asyncio.wait_for(pending_payments[payment_hash].wait(), timeout=300)

            # Payment settled, yield the success message
            yield f"data: {json.dumps({'status': 'settled'})}\n\n"
        finally:
            # Clean up
            pending_payments.pop(payment_hash, None)

    async def wait_for_payment(payment_hash: str):
        start_time = asyncio.get_event_loop().time()
        while True:
            payment = get_payment(payment_hash)
            
            if payment['state'] == 'SETTLED':
                pending_payments[payment_hash].set()
                break

            if asyncio.get_event_loop().time() - start_time > 300:
                # 5 minutes timeout
                break

            await asyncio.sleep(3)  # Wait for 3 seconds before checking again

    @app.get("/get_config")
    def get_config():
        models = list_models()
        return JSONResponse(content={
            "models": models,
            "min_satoshi_amount": config.MIN_SATOSHI_QNT,
            "max_text_length": config.MAX_TEXT_LENGTH,
            # Add any other configuration parameters here
        })
    
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

    @app.get("/events")
    def widget_events():
        return StreamingResponse(get_events(), media_type="text/event-stream")