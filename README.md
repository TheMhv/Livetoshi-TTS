# Livesatoshi API Server
The API server for [LiveSatoshi](https://github.com/TheMhv/LiveSatoshi)

## Instalation

> Recommended python version: 3.10

```bash
$ pip install -r requirements.txt
```
> [!NOTE]
> If you have any problems with the omegaconf version, try downgrading pip to version 24.0 `python.exe -m pip install pip==24.0`

### GPU installation (Recommended)
Install the PyTorch-related core dependencies

You need to specify the cuda version corresponding to pytorch:

> https://pytorch.org/get-started/locally

### Get the Access Token

You will need to create an access token with the `invoices:read` permission in your getalby account.

> https://getalby.com/developer

### Config your .env

Copy the example .env
```bash
$ cp .env.example .env
```

Set the `ALBY_TOKEN` with your getalby account access token.

Change the another values according to your preference.

## Usage

> You will need to configure the server address in the webhook of your getalby account to receive payment events.
> REMEMBER TO ADD THE `/receive` ROUTE

* Download some RVC models
    - You can find some at https://applio.org/models
* Extract and put your models into `MODELS_DIR`
* Run the server:

```bash
$ python main.py
```

* And set the url with `/widget` route for your streaming software

## Tips

### Documentation

FastAPI provides route documentation automatically.

You can check the `/docs` route for [Swagger UI](https://github.com/swagger-api/swagger-ui) format or the `/redoc` route for [ReDoc](https://github.com/Redocly/redoc) format.

### Model configuration

You can configure some parameters for TTS and RVC models.

You must create a `params.json` file inside the folder of the model you want to configure.

Here is an example of the `params.json` file:
```json
{
    "tts": {
        "voice": "pt-BR-AntonioNeural",
        "rate": "+0%",
        "volume": "+0%",
        "pitch": "+0Hz"
    },
    "rvc": {
        "f0method": "rmvpe",
        "f0up_key": 0,
        "index_rate": 0.75,
        "filter_radius": 3,
        "resample_sr": 0,
        "rms_mix_rate": 0.25,
        "protect": 0.33
    }
}
```
