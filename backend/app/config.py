from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Google Cloud Configuration
    PROJECT_ID: str = "pipeline-video-ia"
    BUCKET_NAME: str = "tiktok-pipeline-artifacts-pipeline-video-ia"
    REGION: str = "us-central1"
    
    # Cloud Function URLs
    SCRIPT_AGENT_URL: Optional[str] = None
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    class Config:
        env_file = ".env"


settings = Settings()
