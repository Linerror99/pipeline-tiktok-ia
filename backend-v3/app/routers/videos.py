"""Router Videos V3 — Génération Veo 3.1 + extensions + statut."""
from fastapi import APIRouter, HTTPException, Depends

from ..models.video import (
    VideoGenerateRequest,
    VideoResponse,
    VideoStatusResponse,
    VideoListResponse,
    VALID_DURATIONS,
)
from ..utils.jwt import get_current_user
from ..services.firestore_service import firestore_service
from ..services.storage import storage_service_v3

router = APIRouter(prefix="/api/v3/videos", tags=["videos"])


@router.post("/generate", response_model=VideoResponse, status_code=201)
async def generate_video(
    data: VideoGenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Lance la génération d'une vidéo Veo 3.1 avec extensions."""
    # Vérifier ownership
    project = firestore_service.get_project(data.project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Charger le scénario
    scenario = firestore_service.get_scenario(data.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scénario non trouvé")
    if scenario.get("status") != "validated":
        raise HTTPException(status_code=400, detail="Scénario non validé")
    if scenario.get("project_id") != data.project_id:
        raise HTTPException(status_code=400, detail="Scénario n'appartient pas au projet")

    target_duration = scenario.get("target_duration", 8)
    if target_duration not in VALID_DURATIONS:
        raise HTTPException(status_code=400, detail=f"Durée invalide: {target_duration}")

    script = scenario.get("script", {})
    if not script.get("blocks"):
        raise HTTPException(status_code=400, detail="Script vide")

    # Charger les personnages référencés
    character_ids = scenario.get("character_ids", [])
    characters = []
    for cid in character_ids:
        char = firestore_service.get_character(cid)
        if char:
            characters.append(char)

    # Créer l'enregistrement vidéo
    video = firestore_service.create_video_record(
        user_id=current_user["id"],
        project_id=data.project_id,
        scenario_id=data.scenario_id,
        target_duration=target_duration,
        script=script,
    )

    # Préparer le script_v3.json avec les refs personnages
    script_data = {
        "video_id": video["id"],
        "project_id": data.project_id,
        "user_id": current_user["id"],
        "target_duration": target_duration,
        "blocks": script["blocks"],
        "characters": [
            {
                "id": c["id"],
                "name": c.get("name", ""),
                "description": c.get("description", ""),
                "image_url": c.get("image_url", ""),
                "traits": c.get("traits", {}),
            }
            for c in characters
        ],
    }

    # Upload script_v3.json → déclenche agent-video-veo31
    storage_service_v3.upload_script_v3(video["id"], script_data)

    return video


@router.get("", response_model=VideoListResponse)
async def list_videos(
    project_id: str = None,
    current_user: dict = Depends(get_current_user),
):
    """Liste les vidéos (optionnellement filtré par projet)."""
    videos = firestore_service.list_videos(
        user_id=current_user["id"],
        project_id=project_id,
    )
    return VideoListResponse(videos=videos, count=len(videos))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Récupère une vidéo."""
    video = firestore_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    if video.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    return video


@router.get("/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(
    video_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Récupère le statut détaillé de la génération."""
    video = firestore_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    if video.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    status = video.get("status", "pending")
    extensions_completed = video.get("extensions_completed", 0)
    extensions_planned = video.get("extensions_planned", 0)

    # Calculer la progression
    if status == "completed":
        progress = 100
        current_step = "Terminé"
    elif status == "failed":
        progress = 0
        current_step = "Échoué"
    elif status == "generating":
        if extensions_planned > 0:
            progress = int(((extensions_completed + 1) / (extensions_planned + 1)) * 100)
            current_step = f"Extension {extensions_completed + 1}/{extensions_planned}"
        else:
            progress = 50
            current_step = "Génération initiale (8s)"
    else:
        progress = 0
        current_step = "En attente"

    return VideoStatusResponse(
        video_id=video_id,
        status=status,
        progress=progress,
        current_step=current_step,
        target_duration=video.get("target_duration", 8),
        extensions_completed=extensions_completed,
        extensions_planned=extensions_planned,
    )


@router.get("/{video_id}/stream")
async def stream_video(
    video_id: str,
    current_user: dict = Depends(get_current_user),
):
    """URL de streaming d'une vidéo."""
    video = firestore_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    if video.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    if video.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Vidéo pas encore prête")

    url = storage_service_v3.get_video_stream_url(video_id)
    return {"stream_url": url}


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    current_user: dict = Depends(get_current_user),
):
    """URL de téléchargement d'une vidéo."""
    video = firestore_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    if video.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    if video.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Vidéo pas encore prête")

    url = storage_service_v3.get_video_download_url(video_id)
    return {"download_url": url}
