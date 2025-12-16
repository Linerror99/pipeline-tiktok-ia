from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Annotated
from ..services.storage import storage_service
from ..services.video_generation import video_generation_service
from ..services.firestore_service import can_create_video, increment_video_count
from ..models.auth import UserInDB
from ..utils.jwt import get_current_user


router = APIRouter(prefix="/videos", tags=["videos"])


class VideoCreateRequest(BaseModel):
    theme: str


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
    Protégé par JWT - nécessite authentification
    """
    if not request.theme or len(request.theme.strip()) == 0:
        raise HTTPException(status_code=400, detail="Le thème ne peut pas être vide")
    
    if len(request.theme) > 500:
        raise HTTPException(status_code=400, detail="Le thème est trop long (max 500 caractères)")
    
    # Vérifier le quota
    if not can_create_video(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Quota atteint : {current_user.video_count}/{current_user.max_videos} vidéos utilisées"
        )
    
    try:
        result = video_generation_service.create_video(request.theme)
        
        # Incrémenter le compteur de vidéos
        increment_video_count(current_user.id)
        
        return VideoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("", response_model=VideosListResponse)
async def list_videos(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    """
    Liste toutes les vidéos générées
    Protégé par JWT - nécessite authentification
    """
    try:
        videos = storage_service.list_videos()
        return VideosListResponse(videos=videos, count=len(videos))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des vidéos: {str(e)}")


@router.get("/{video_id}/status")
async def get_video_status(
    video_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    """
    Récupère le statut d'une vidéo en cours de génération
    Protégé par JWT - nécessite authentification
    """
    try:
        status = storage_service.get_video_status(video_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    """
    Récupère l'URL de téléchargement d'une vidéo (force le téléchargement du fichier)
    Protégé par JWT - nécessite authentification
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
async def stream_video(
    video_id: str,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
):
    """
    Récupère l'URL de streaming d'une vidéo (lecture dans le navigateur)
    Protégé par JWT - nécessite authentification
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
