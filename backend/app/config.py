from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    ROBOFLOW_API_KEY: str = os.getenv("ROBOFLOW_API_KEY", "YOUR_ROBOFLOW_API_KEY_PLACEHOLDER")
    ROBOFLOW_MODEL_ID: str = os.getenv("ROBOFLOW_MODEL_ID", "your_model_project/version") # e.g., "adr/6"
    
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()