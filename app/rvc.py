import tempfile
import os
import base64
from rvc_python.infer import RVCInference
from app.models import Model
from app.config import load_config

config = load_config()

async def rvc(model: Model, audio_path: str):
    rvc_params = model.params.rvc if model.params else None

    rvc = RVCInference(
        models_dir=config.MODELS_DIR,
        device=config.DEVICE
    )
    
    rvc.set_params(
        f0method=rvc_params.f0method,
        f0up_key=rvc_params.f0up_key,
        index_rate=rvc_params.index_rate,
        filter_radius=rvc_params.filter_radius,
        resample_sr=rvc_params.resample_sr,
        rms_mix_rate=rvc_params.rms_mix_rate,
        protect=rvc_params.protect
    )

    tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    output_path = tmp_output.name

    rvc.load_model(model.name, "v2")
    rvc.infer_file(audio_path, output_path)
    rvc.unload_model()

    with open(output_path, "rb") as f:
        audio_data = base64.b64encode(f.read())

    tmp_output.close()
    os.unlink(tmp_output.name)
    
    return audio_data