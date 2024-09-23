from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, StreamingResponse
from starlette.responses import FileResponse
from rvc_python.infer import RVCInference
from pydantic import BaseModel
from dotenv import load_dotenv
from glob import glob
import requests
import edge_tts
import tempfile
import base64
import json
import os

load_dotenv()

def get_model(name: str) -> dict | None:
    for model_dir in glob(os.path.join(str(os.getenv("MODELS_DIR", 'models')), "*")):
        if os.path.isdir(model_dir):
            model_name = os.path.basename(model_dir)
            
            if model_name != name:
                continue

            pth_file = glob(os.path.join(model_dir, "*.pth"))
            index_file = glob(os.path.join(model_dir, "*.index"))
            image_file = glob(os.path.join(model_dir, "image.*"))
            params_file = glob(os.path.join(model_dir, "params.json"))

            try:
                params_file = json.load(open(params_file[0], 'r'))
            except:
                params_file if params_file else None

            if pth_file:
                model = {
                    "name": model_name,
                    "pth": pth_file[0]
                }

                if index_file:
                    model['index'] = index_file[0],
                
                if image_file:
                    model['image'] = image_file[0]
                
                if params_file:
                    model['params'] = params_file
                
                return model
            
async def tts(model: dict | None, text: str):
    tts_params = {
        'voice': "pt-BR-ThalitaNeural",
        'rate': "+0%",
        'volume': "+0%",
        'pitch': "+0Hz"
    }

    if not model:
        model = {}

    tts_params = model.get('params', {}).get('tts', tts_params)

    VOICE = tts_params.get('voice', "pt-BR-ThalitaNeural")
    RATE = tts_params.get('rate', "+0%")
    VOLUME = tts_params.get('volume', "+0%")
    PITCH = tts_params.get('pitch', "+0Hz")

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=RATE,
        volume=VOLUME,
        pitch=PITCH
    )

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    await communicate.save(tmp_file.name)
    return tmp_file

async def rvc(model: dict, audio_path: str):
    default_rvc = {
        'f0method': "rmvpe",
        'f0up_key': 0,
        'index_rate': 0.75,
        'filter_radius': 3,
        'resample_sr': 0,
        'rms_mix_rate': 0.25,
        'protect': 0.33
    }
    rvc_params = model.get('params', {}).get('rvc', default_rvc)

    METHOD = rvc_params.get('f0method', "rmvpe")
    UP_KEY = rvc_params.get('f0up_key', 0)
    INDEX_RATE = rvc_params.get('index_rate', 0.75)
    FILTER_RADIUS = rvc_params.get('filter_radius', 3)
    RESAMPLE_SR = rvc_params.get('resample_sr', 0)
    RMS_MIX_RATE = rvc_params.get('rms_mix_rate', 0.25)
    PROTECT = rvc_params.get('protect', 0.33)

    rvc = RVCInference(
        models_dir=str(os.getenv("MODELS_DIR", 'models')),
        device=str(os.getenv("DEVICE", 'cuda:0'))
    )
    
    rvc.set_params(
        f0method=METHOD,
        f0up_key=UP_KEY,
        index_rate=INDEX_RATE,
        filter_radius=FILTER_RADIUS,
        resample_sr=RESAMPLE_SR,
        rms_mix_rate=RMS_MIX_RATE,
        protect=PROTECT
    )

    tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    output_path = tmp_output.name

    rvc.load_model(model['name'], "v2")
    rvc.infer_file(audio_path, output_path)
    rvc.unload_model()

    audio_data = base64.b64encode(tmp_output.read())

    tmp_output.close()
    os.unlink(tmp_output.name)
    
    return audio_data

async def generate(text: str, model_name: str | None):
    # Get model params
    model = get_model(model_name)

    # Generate TTS audio
    tts_file = await tts(model=model, text=text)

    if not model:
        audio_data = base64.b64encode(tts_file.read())
        
        tts_file.close()
        os.unlink(tts_file.name)

        return audio_data

    # Generate RVC audio
    return await rvc(model=model, audio_path=tts_file.name)

def getPayment(payment_hash: str):
    headers = {"Authorization": f"Bearer {str(os.getenv('ALBY_TOKEN'))}"}
    response = requests.get(f"https://api.getalby.com/invoices/{payment_hash}", headers=headers)
    return response.json()

class WebhookRequest(BaseModel):
    payment_hash: str

def setup_routes(app: FastAPI):
    async def getEvents():
        while True:
            event = await app.queue.get()
            yield f"event: Message\ndata: {event}\n\n"

    @app.get("/models")
    def list_models():
        models = []

        for model_dir in glob(os.path.join(str(os.getenv("MODELS_DIR"), 'models'), "*")):
            if os.path.isdir(model_dir):
                model_name = os.path.basename(model_dir)

                pth_file = glob(os.path.join(model_dir, "*.pth"))
                image_file = glob(os.path.join(model_dir, "image.*"))
                
                if pth_file:
                    models.append({
                        "name": model_name,
                        "image": image_file[0] if image_file else None
                    })

        return JSONResponse(content=models)
    
    @app.post("/receive")
    async def receive_webhook(request: WebhookRequest):
        try:
            payment = getPayment(request.payment_hash)

            if not payment['metadata']['text']:
                raise HTTPException(status_code=400, detail="No text provided")
            
            if int(payment['amount']) < int(os.getenv("MIN_SATOSHI_QNT", 100)):
                raise HTTPException(status_code=400, detail="Minimum payment not made")

            if payment['state'] != 'SETTLED':
                raise HTTPException(status_code=400, detail="Payment was not made")
            
            text = payment['metadata']['text']

            if text:
                text = text[:int(os.getenv("MAX_TEXT_LENGHT", 200))]

            amount = payment.get('amount', 'alguns')
            name = payment.get('metadata', {}).get('name', 'Anônimo')
            model = payment.get('metadata', {}).get('model', None)

            text = f"{name} enviou {amount} satoshis: {text}"

            audio_data = await generate(
                text=text,
                model_name=model
            )

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
    def widgetEvents():
        return StreamingResponse(getEvents(), media_type="text/event-stream")

def create_app():
    app = FastAPI()

    # Add CORS middleware
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_routes(app)
    return app
