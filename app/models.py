from pydantic import BaseModel

class WebhookRequest(BaseModel):
    payment_hash: str

class TTSParams(BaseModel):
    voice: str = "pt-BR-ThalitaNeural"
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"

class RVCParams(BaseModel):
    f0method: str = "rmvpe"
    f0up_key: int = 0
    index_rate: float = 0.75
    filter_radius: int = 3
    resample_sr: int = 0
    rms_mix_rate: float = 0.25
    protect: float = 0.33

class ModelParams(BaseModel):
    tts: TTSParams = TTSParams()
    rvc: RVCParams = RVCParams()

class Model(BaseModel):
    name: str
    pth: str
    index: str | None = None
    image: str | None = None
    params: ModelParams | None = None