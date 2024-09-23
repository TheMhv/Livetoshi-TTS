# app/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class Settings(BaseSettings):
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", 8000))
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    MODELS_DIR: str = os.getenv("MODELS_DIR", "models")
    DEVICE: str = os.getenv("DEVICE", "cuda:0")
    MIN_SATOSHI_QNT: int = int(os.getenv("MIN_SATOSHI_QNT", 100))
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", 200))
    ALBY_TOKEN: str = os.getenv("ALBY_TOKEN", "")

def load_config() -> Settings:
    return Settings()