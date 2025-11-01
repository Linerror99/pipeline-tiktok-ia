from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from ..services.storage import storage_service
from ..services.video_generation import video_generation_service


router = APIRouter(prefix="/api/videos", tags=["videos"])


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
async def create_video(request: VideoCreateRequest):
    """
    Déclenche la génération d'une nouvelle vidéo TikTok
    """
    if not request.theme or len(request.theme.strip()) == 0:
        raise HTTPException(status_code=400, detail="Le thème ne peut pas être vide")
    
    if len(request.theme) > 500:
        raise HTTPException(status_code=400, detail="Le thème est trop long (max 500 caractères)")
    
    try:
        result = video_generation_service.create_video(request.theme)
        return VideoResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("", response_model=VideosListResponse)
async def list_videos():
    """
    Liste toutes les vidéos générées
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
    """
    try:
        status = storage_service.get_video_status(video_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")


@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """
    Récupère l'URL de téléchargement d'une vidéo
    """
    try:
        url = storage_service.get_video_url(video_id)
        if not url:
            raise HTTPException(status_code=404, detail="Vidéo non trouvée")
        
        return {"video_id": video_id, "download_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'URL: {str(e)}")
