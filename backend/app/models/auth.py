"""
Modèles Pydantic pour l'authentification
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """Requête d'inscription"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 caractères")
    access_code: str = Field(..., min_length=8, max_length=8, description="Code d'accès actuel")


class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: EmailStr
    password: str


class VerifyCodeRequest(BaseModel):
    """Vérification du code d'accès"""
    code: str = Field(..., min_length=8, max_length=8)


class TokenResponse(BaseModel):
    """Réponse avec token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """Informations utilisateur (sans password)"""
    id: str
    email: str
    is_admin: bool
    video_count: int
    max_videos: int
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    """Utilisateur en base de données"""
    id: str
    email: str
    password_hash: str
    is_admin: bool = False
    video_count: int = 0
    max_videos: int = 2  # 2 pour les utilisateurs normaux, -1 pour admin (illimité)
    created_at: datetime
    last_login: Optional[datetime] = None
