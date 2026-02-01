from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Dict, Annotated
from ..services.storage import storage_service
from ..services.video_generation import video_generation_service
from ..services.firestore_service import can_create_video, increment_video_count, verify_access_code
from ..models.auth import UserInDB
from ..utils.jwt import get_current_user


router = APIRouter(prefix="/videos", tags=["videos"])


class VideoCreateRequest(BaseModel):
    theme: str
    access_code: str = Field(..., min_length=8, max_length=8, description="Code d'accès actuel")
    target_duration: int = Field(default=36, ge=8, le=78, description="Durée cible en secondes (8-78s)")
    style: str = Field(default="informative", description="Style visuel (informative, humorous, dramatic, inspiring)")
    language: str = Field(default="fr", description="Langue (fr, en, es)")


class VideoResponse(BaseModel):
    video_id: str
    status: str
    message: str
    theme: str


class VideosListResponse(BaseModel):
    videos: List[Dict]
    count: int


@router.post("/create", response_model=VideoResponse)
async def create_video(
    request: VideoCreateRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    """
    Déclenche la génération d'une nouvelle vidéo TikTok
    Protégé par JWT + Code d'accès - nécessite authentification ET code valide
    """
    if not request.theme or len(request.theme.strip()) == 0:
        raise HTTPException(status_code=400, detail="Le thème ne peut pas être vide")
    
    if len(request.theme) > 500:
        raise HTTPException(status_code=400, detail="Le thème est trop long (max 500 caractères)")
    
    # Vérifier le code d'accès
    if not verify_access_code(request.access_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code d'accès invalide. Il change toutes les heures."
        )
    
    # Vérifier le quota
    if not can_create_video(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Quota atteint : {current_user.video_count}/{current_user.max_videos} vidéos utilisées"
        )
    
    try:
        result = video_generation_service.create_video(
            theme=request.theme,
            target_duration=request.target_duration,
            style=request.style,
            language=request.language
        )
        
        # Incrémenter le compteur de vidéos
        increment_video_count(current_user.id)
        
        return VideoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("", response_model=VideosListResponse)
async def list_videos():
    """
    Liste toutes les vidéos générées
    Endpoint public - pas d'authentification requise
    """
    try:
        videos = storage_service.list_videos()
        return VideosListResponse(videos=videos, count=len(videos))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des vidéos: {str(e)}")


@router.get("/{video_id}/status")
async def get_video_status(video_id: str):
    """
    Récupère le statut d'une vidéo en cours de génération
    Endpoint public - pas d'authentification requise
    """
    try:
        status = storage_service.get_video_status(video_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")


@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """
    Récupère l'URL de téléchargement d'une vidéo (force le téléchargement du fichier)
    Endpoint public - pas d'authentification requise
    """
    try:
        url = storage_service.get_video_url(video_id, expiration_minutes=60)
        if not url:
            raise HTTPException(status_code=404, detail="Vidéo non trouvée")
        
        return {"video_id": video_id, "download_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'URL: {str(e)}")


@router.get("/{video_id}/stream")
async def stream_video(video_id: str):
    """
    Récupère l'URL de streaming d'une vidéo (lecture dans le navigateur)
    Endpoint public - pas d'authentification requise
    """
    try:
        url = storage_service.get_video_stream_url(video_id)
        if not url:
            raise HTTPException(status_code=404, detail="Vidéo non trouvée")
        
        return {"video_id": video_id, "stream_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'URL de streaming: {str(e)}")
