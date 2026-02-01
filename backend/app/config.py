import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Google Cloud Configuration
    PROJECT_ID: str = "reetik-project"
    BUCKET_NAME: str = "tiktok-pipeline-artifacts-reetik-project"
    REGION: str = "us-central1"
    
    # Cloud Function URLs
    SCRIPT_AGENT_URL: Optional[str] = None
    ACCESS_CODE_FUNCTION_URL: Optional[str] = None
    # Path to a service account JSON key file (for local/dev). When provided,
    # this value will be set into the environment as GOOGLE_APPLICATION_CREDENTIALS
    # so google-cloud-storage can pick it up automatically.
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # Autoriser les requêtes depuis le frontend conteneurisé
        "http://frontend",
    ]
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"


settings = Settings()

# If a credentials JSON path is provided in settings, export it so the
# Google Cloud client libraries can use it for signing URLs and other
# authenticated operations. This is safe for local/dev where a key file
# is present; in production prefer Workload Identity / implicit credentials.
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS)
