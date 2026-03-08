"""Modèles Pydantic pour l'authentification V3 (Firebase Auth + JWT interne)."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class FirebaseLoginRequest(BaseModel):
    """Token ID Firebase envoyé par le frontend après Google Sign-In."""
    id_token: str = Field(..., description="Firebase ID token from Google Sign-In")


class VerifyCodeRequest(BaseModel):
    """Code d'accès post-login (garde-fou anti-abus)."""
    code: str = Field(..., min_length=8, max_length=8)


class TokenResponse(BaseModel):
    """Réponse avec JWT V3 interne."""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """Informations utilisateur (public)."""
    id: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    is_admin: bool = False
    video_count: int = 0
    project_count: int = 0
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserInDB(BaseModel):
    """Utilisateur en Firestore."""
    id: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    firebase_uid: str = ""
    is_admin: bool = False
    video_count: int = 0
    project_count: int = 0
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
