# Livesatoshi API Server
An API server for LiveSatoshi project

## Instalation

> Recommended python version: 3.10

```bash
pip install -r requirements.txt
```
### GPU installation (Recommended)
Install the PyTorch-related core dependencies

You need to specify the cuda version corresponding to pytorch:

> https://pytorch.org/get-started/locally

### Get Alby token

You will need to create an access token with the `invoices:read` permission in your getalby account.

> https://getalby.com/developer

### Config your .env

Copy the example .env
```bash
cp .env.example .env
```

Set the `ALBY_TOKEN` with your getalby account access token.

Change the another values according to your preference.

## Usage

To run the server, just run:

```bash
python run.py
```