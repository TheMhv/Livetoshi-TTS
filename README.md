# Livesatoshi API Server
An API server for LiveSatoshi project

## Instalation

> Recommended python version: 3.10

```bash
$ pip install -r requirements.txt
```
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
$ python run.py
```

* And set the url with `/widget` route for your streaming software