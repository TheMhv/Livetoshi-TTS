import os
import json
from glob import glob
from app.models import Model, ModelParams
from app.config import load_config

config = load_config()

def get_model(name: str) -> Model | None:
    for model_dir in glob(os.path.join(config.MODELS_DIR, "*")):
        if os.path.isdir(model_dir):
            model_name = os.path.basename(model_dir)
            
            if model_name != name:
                continue

            pth_file = glob(os.path.join(model_dir, "*.pth"))
            index_file = glob(os.path.join(model_dir, "*.index"))
            image_file = glob(os.path.join(model_dir, "image.*"))
            params_file = glob(os.path.join(model_dir, "params.json"))

            if pth_file:
                model = Model(
                    name=model_name,
                    pth=pth_file[0],
                    index=index_file[0] if index_file else None,
                    image=image_file[0] if image_file else None
                )

                if params_file:
                    try:
                        with open(params_file[0], 'r') as f:
                            params = json.load(f)
                        model.params = ModelParams(**params)
                    except json.JSONDecodeError:
                        pass

                return model
    
    return None

def list_models():
    models = []
    for model_dir in glob(os.path.join(config.MODELS_DIR, "*")):
        if os.path.isdir(model_dir):
            model_name = os.path.basename(model_dir)
            model = get_model(model_name)
            if model:
                models.append({
                    "name": model.name,
                    "image": model.image
                })
    return models