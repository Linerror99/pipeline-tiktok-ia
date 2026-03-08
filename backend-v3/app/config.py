import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Google Cloud
    PROJECT_ID: str = "reetik-project"
    REGION: str = "us-central1"

    # Firestore V3 (base de données séparée de V2)
    FIRESTORE_DATABASE: str = "reetik-v3"

    # Buckets V3 (séparés de V2)
    BUCKET_NAME_V3: str = "reetik-v3-artifacts"
    BUCKET_UPLOADS_V3: str = "reetik-v3-uploads"
    BUCKET_THUMBNAILS_V3: str = "reetik-v3-thumbnails"

    # Cloud Function URLs (V3 agents)
    SCRIPT_AGENT_URL: Optional[str] = None

    # Firebase Auth
    FIREBASE_PROJECT_ID: str = "reetik-project"

    # Credentials (local dev only)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # JWT V3 interne (post-Firebase auth)
    JWT_SECRET_KEY: str = "v3-secret-key-change-in-production-min-32-chars!!"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://frontend-v3",
    ]

    # Email notifications (optionnel)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    NOTIFICATION_FROM_EMAIL: str = "noreply@reetik.app"

    class Config:
        env_file = ".env"


settings = Settings()

if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ.setdefault(
        "GOOGLE_APPLICATION_CREDENTIALS",
        settings.GOOGLE_APPLICATION_CREDENTIALS,
    )
