"""Router Videos V3 — Génération Veo 3.1 + BackgroundTask + WebSocket."""
import asyncio
import json
import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect

from ..models.video import (
    VALID_DURATIONS,
    VideoGenerateRequest,
    VideoListResponse,
    VideoResponse,
    VideoStatusResponse,
)
from ..services import video_service
from ..services.firestore_service import firestore_service
from ..services.storage import storage_service_v3
from ..utils.jwt import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v3/videos", tags=["videos"])


@router.post("/generate", response_model=VideoResponse, status_code=201)
async def generate_video(
    data: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Lance la génération Veo 3.1 en tâche de fond."""
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

    # Créer l'enregistrement vidéo en Firestore
    video = firestore_service.create_video_record(
        user_id=current_user["id"],
        project_id=data.project_id,
        scenario_id=data.scenario_id,
        target_duration=target_duration,
        script=script,
    )

    # Lancer la génération en arrière-plan (continue même si le client déconnecte)
    background_tasks.add_task(
        video_service.generate_video_background,
        video_id=video["id"],
        project_id=data.project_id,
        scenario_id=data.scenario_id,
        target_duration=target_duration,
        blocks=script.get("blocks", []),
        characters=[
            {
                "id": c.get("id", ""),
                "name": c.get("name", ""),
                "description": c.get("description", ""),
                "image_url": c.get("image_url", ""),
                "gcs_path": c.get("gcs_path", ""),
                "traits": c.get("traits", {}),
                "ai_description": c.get("ai_description", ""),
            }
            for c in characters
        ],
    )

    return video


@router.get("", response_model=VideoListResponse)
async def list_videos(
    project_id: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
):
    """Liste les vidéos (optionnellement filtré par projet)."""
    videos = firestore_service.list_videos(project_id=project_id)
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
    progress = video.get("progress", 0)
    current_step = video.get("current_step", "En attente")

    return VideoStatusResponse(
        video_id=video_id,
        status=status,
        progress=progress,
        current_step=current_step,
        target_duration=video.get("target_duration", 8),
        extensions_completed=extensions_completed,
        extensions_planned=extensions_planned,
    )


@router.websocket("/{video_id}/ws")
async def video_status_ws(
    websocket: WebSocket,
    video_id: str,
):
    """WebSocket : stream les mises à jour de statut de génération toutes les 5s.

    Authentification via token en query param: /ws?token=<jwt>
    Le WS continue de streamer même si le client reconnecte plus tard.
    Envoie le snapshot Firestore jusqu'à status=completed|failed.
    """
    # Auth via query param (WS ne supporte pas les headers Authorization)
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Token manquant")
        return

    from ..utils.jwt import decode_token
    user_data = decode_token(token)
    if user_data is None:
        await websocket.close(code=4001, reason="Token invalide")
        return

    video = firestore_service.get_video(video_id)
    if not video or video.get("user_id") != user_data.get("sub"):
        await websocket.close(code=4003, reason="Accès non autorisé")
        return

    await websocket.accept()
    logger.info(f"WS connecté pour video {video_id}")

    try:
        while True:
            video = firestore_service.get_video(video_id)
            if not video:
                await websocket.send_text(json.dumps({"error": "Vidéo introuvable"}))
                break

            status = video.get("status", "pending")
            payload = {
                "video_id": video_id,
                "status": status,
                "progress": video.get("progress", 0),
                "current_step": video.get("current_step", ""),
                "extensions_completed": video.get("extensions_completed", 0),
                "extensions_planned": video.get("extensions_planned", 0),
                "video_url": video.get("video_url"),
                "error": video.get("error"),
            }
            await websocket.send_text(json.dumps(payload))

            if status in ("completed", "failed"):
                break

            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info(f"WS déconnecté pour video {video_id} (client fermé)")
    except Exception as e:
        logger.error(f"WS erreur video {video_id}: {e}")
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass


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


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Supprime une vidéo (enregistrement Firestore uniquement)."""
    video = firestore_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    if video.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    firestore_service.delete_video(video_id)


@router.post("/{video_id}/retry", response_model=VideoResponse)
async def retry_video(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Relance la génération d'une vidéo en échec."""
    video = firestore_service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo non trouvée")
    if video.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    if video.get("status") not in ("failed", "error"):
        raise HTTPException(status_code=400, detail="Seules les vidéos en échec peuvent être relancées")

    # Recharger le scénario et les personnages
    scenario = firestore_service.get_scenario(video["scenario_id"])
    if not scenario:
        raise HTTPException(status_code=404, detail="Scénario introuvable")

    script = scenario.get("script", {})
    if not script.get("blocks"):
        raise HTTPException(status_code=400, detail="Script vide")

    character_ids = scenario.get("character_ids", [])
    characters = []
    for cid in character_ids:
        char = firestore_service.get_character(cid)
        if char:
            characters.append(char)

    # Remettre le statut à "generating"
    firestore_service.update_video(video_id, {
        "status": "generating",
        "progress": 0,
        "current_step": "Relance en cours...",
        "error": None,
        "video_url": None,
    })

    background_tasks.add_task(
        video_service.generate_video_background,
        video_id=video_id,
        project_id=video["project_id"],
        scenario_id=video["scenario_id"],
        target_duration=video.get("target_duration", 8),
        blocks=script.get("blocks", []),
        characters=[
            {
                "id": c.get("id", ""),
                "name": c.get("name", ""),
                "description": c.get("description", ""),
                "image_url": c.get("image_url", ""),
                "gcs_path": c.get("gcs_path", ""),
                "traits": c.get("traits", {}),
                "ai_description": c.get("ai_description", ""),
            }
            for c in characters
        ],
    )

    return firestore_service.get_video(video_id)
