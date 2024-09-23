import edge_tts
import tempfile
from app.models import Model, TTSParams

async def tts(model: Model | None, text: str):
    tts_params = TTSParams()

    if model and model.params:
        tts_params = model.params.tts

    communicate = edge_tts.Communicate(
        text=text,
        voice=tts_params.voice,
        rate=tts_params.rate,
        volume=tts_params.volume,
        pitch=tts_params.pitch
    )

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    await communicate.save(tmp_file.name)
    return tmp_file