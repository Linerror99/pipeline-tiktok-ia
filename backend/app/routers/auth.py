"""
Routes d'authentification
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated

from ..models.auth import (
    RegisterRequest,
    LoginRequest,
    VerifyCodeRequest,
    TokenResponse,
    UserResponse,
    UserInDB,
)
from ..services.firestore_service import (
    verify_access_code,
    get_user_by_email,
    create_user,
    update_last_login,
)
from ..utils.jwt import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    user_to_response,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/verify-code", status_code=status.HTTP_200_OK)
async def verify_code(request: VerifyCodeRequest):
    """
    Vérifie si le code d'accès est valide (pour afficher le formulaire d'inscription)
    """
    is_valid = verify_access_code(request.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code d'accès invalide. Il change toutes les heures."
        )
    
    return {"valid": True, "message": "Code valide"}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Inscription d'un nouvel utilisateur (pas de vérification de code ici)
    """
    # 1. Vérifier si l'email existe déjà
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte existe déjà avec cet email"
        )
    
    # 2. Créer l'utilisateur
    password_hashed = hash_password(request.password)
    new_user = create_user(request.email, password_hashed, is_admin=False)
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du compte"
        )
    
    # 3. Mettre à jour la date de connexion
    update_last_login(new_user.id)
    
    # 4. Créer le token JWT
    access_token = create_access_token(new_user)
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_response(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Connexion d'un utilisateur existant
    """
    # 1. Vérifier l'existence de l'utilisateur
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # 2. Vérifier le mot de passe
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # 3. Mettre à jour la date de connexion
    update_last_login(user.id)
    
    # 4. Créer le token JWT
    access_token = create_access_token(user)
    
    return TokenResponse(
        access_token=access_token,
        user=user_to_response(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[UserInDB, Depends(get_current_user)]):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return user_to_response(current_user)
