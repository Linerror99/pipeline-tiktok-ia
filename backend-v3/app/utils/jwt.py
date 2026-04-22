"""JWT V3 — Génération et vérification de tokens internes post-Firebase Auth."""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import settings
from ..models.auth import UserInDB, UserResponse

security = HTTPBearer()


def create_access_token(user: UserInDB) -> str:
    """Crée un JWT V3 interne pour un utilisateur authentifié via Firebase."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRE_DAYS)
    payload = {
        "sub": user.id,
        "email": user.email,
        "firebase_uid": user.firebase_uid,
        "is_admin": user.is_admin,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Décode et vérifie un JWT V3."""
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dépendance FastAPI : récupère l'utilisateur depuis le JWT V3."""
    from ..services.firestore_service import get_user_by_id

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )

    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
        )

    return user.model_dump() if hasattr(user, "model_dump") else user


def user_to_response(user) -> UserResponse:
    """Convertit un UserInDB ou un dict en UserResponse."""
    if isinstance(user, dict):
        return UserResponse(
            id=user["id"],
            email=user.get("email", ""),
            display_name=user.get("display_name"),
            photo_url=user.get("photo_url"),
            is_admin=user.get("is_admin", False),
            video_count=user.get("video_count", 0),
            project_count=user.get("project_count", 0),
            created_at=user.get("created_at"),
            last_login=user.get("last_login"),
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        photo_url=user.photo_url,
        is_admin=user.is_admin,
        video_count=user.video_count,
        project_count=user.project_count,
        created_at=user.created_at,
        last_login=user.last_login,
    )
