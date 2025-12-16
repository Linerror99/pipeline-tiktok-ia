"""
Utilitaires JWT pour l'authentification
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import settings
from ..models.auth import UserInDB, UserResponse
from ..services.firestore_service import get_user_by_id

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user: UserInDB) -> str:
    """Crée un token JWT pour un utilisateur"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)
    
    payload = {
        "sub": user.id,  # Subject = user ID
        "email": user.email,
        "is_admin": user.is_admin,
        "exp": expire
    }
    
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Décode et vérifie un token JWT"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """
    Dépendance FastAPI pour récupérer l'utilisateur authentifié
    Usage: current_user: UserInDB = Depends(get_current_user)
    """
    token = credentials.credentials
    
    # Décoder le token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Récupérer l'utilisateur
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def user_to_response(user: UserInDB) -> UserResponse:
    """Convertit UserInDB en UserResponse (sans password_hash)"""
    return UserResponse(
        id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        video_count=user.video_count,
        max_videos=user.max_videos,
        created_at=user.created_at,
        last_login=user.last_login
    )
