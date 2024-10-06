import base64
import os
from app.rvc import rvc
from app.tts import tts
from app.utils import get_model

async def audiogen(text: str, model_name: str | None):
    print(text, model_name)

    model = get_model(model_name) if model_name else None
    tts_file = await tts(model=model, text=text)

    if not model:
        with open(tts_file.name, "rb") as f:
            audio_data = base64.b64encode(f.read())
        
        os.unlink(tts_file.name)
        return audio_data

    return await rvc(model=model, audio_path=tts_file.name)