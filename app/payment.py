import requests
from app.config import load_config

config = load_config()

def get_payment(payment_hash: str):
    headers = {"Authorization": f"Bearer {config.ALBY_TOKEN}"}
    response = requests.get(f"https://api.getalby.com/invoices/{payment_hash}", headers=headers)
    return response.json()

def create_payment(amount: int, metadata: dict):
    headers = {"Authorization": f"Bearer {config.ALBY_TOKEN}"}
    data = {
        "amount": amount,
        "unit": "sat",
        "metadata": metadata
    }
    response = requests.post("https://api.getalby.com/invoices", json=data, headers=headers)
    return response.json()