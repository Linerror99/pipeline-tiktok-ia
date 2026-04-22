"""Router Auth V3 — Firebase Auth Google Sign-In + access code."""
from fastapi import APIRouter, HTTPException, Depends

from ..models.auth import (
    FirebaseLoginRequest,
    VerifyCodeRequest,
    TokenResponse,
    UserResponse,
)
from ..utils.firebase import verify_firebase_token
from ..utils.jwt import create_access_token, get_current_user, user_to_response
from ..services.firestore_service import firestore_service

router = APIRouter(prefix="/api/v3/auth", tags=["auth"])


@router.post("/verify-code")
async def verify_access_code(req: VerifyCodeRequest):
    """Vérifie le code d'accès (gate anti-abus, avant login)."""
    is_valid = firestore_service.verify_access_code(req.code)
    if not is_valid:
        raise HTTPException(status_code=403, detail="Code d'accès invalide")
    return {"valid": True}


@router.post("/login", response_model=TokenResponse)
async def login_with_firebase(req: FirebaseLoginRequest):
    """Login via Firebase ID token (Google Sign-In)."""
    # Vérifier le token Firebase
    decoded = verify_firebase_token(req.id_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Token Firebase invalide")

    firebase_uid = decoded.get("uid")
    email = decoded.get("email", "")
    display_name = decoded.get("name", email.split("@")[0] if email else "User")
    photo_url = decoded.get("picture", "")

    # Chercher ou créer l'utilisateur
    user = firestore_service.get_user_by_firebase_uid(firebase_uid)
    if not user:
        user = firestore_service.create_user_from_firebase(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            photo_url=photo_url,
        )
    else:
        firestore_service.update_last_login(user.id)

    # Générer JWT interne V3
    token = create_access_token(user)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_to_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Retourne les infos de l'utilisateur connecté."""
    return user_to_response(current_user)
