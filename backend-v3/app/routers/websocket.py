"""Router WebSocket V3 — Suivi temps réel de la génération vidéo."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import asyncio
import json
import logging

from ..utils.jwt import decode_token
from ..services.firestore_service import firestore_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManagerV3:
    """Gestionnaire de connexions WebSocket V3."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, video_id: str, websocket: WebSocket):
        await websocket.accept()
        if video_id not in self.active_connections:
            self.active_connections[video_id] = []
        self.active_connections[video_id].append(websocket)
        logger.info(f"WS connecté: video={video_id}, total={len(self.active_connections[video_id])}")

    def disconnect(self, video_id: str, websocket: WebSocket):
        if video_id in self.active_connections:
            self.active_connections[video_id].remove(websocket)
            if not self.active_connections[video_id]:
                del self.active_connections[video_id]
        logger.info(f"WS déconnecté: video={video_id}")

    async def send_update(self, video_id: str, data: dict):
        if video_id in self.active_connections:
            disconnected = []
            for ws in self.active_connections[video_id]:
                try:
                    await ws.send_json(data)
                except Exception:
                    disconnected.append(ws)
            for ws in disconnected:
                self.active_connections[video_id].remove(ws)


manager = ConnectionManagerV3()


@router.websocket("/ws/v3/video/{video_id}")
async def websocket_video_status(
    websocket: WebSocket,
    video_id: str,
    token: str = Query(default=None),
):
    """WebSocket pour suivre le statut d'une vidéo en temps réel."""
    # Authentifier via token JWT dans query params
    if not token:
        await websocket.close(code=4001, reason="Token manquant")
        return

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        await websocket.close(code=4001, reason="Token invalide")
        return

    # Vérifier ownership
    video = firestore_service.get_video(video_id)
    if not video or video.get("user_id") != user_id:
        await websocket.close(code=4003, reason="Accès non autorisé")
        return

    await manager.connect(video_id, websocket)

    try:
        # Envoyer le statut initial
        await websocket.send_json({
            "type": "status",
            "video_id": video_id,
            "status": video.get("status", "pending"),
            "extensions_completed": video.get("extensions_completed", 0),
            "extensions_planned": video.get("extensions_planned", 0),
        })

        # Polling Firestore pour les mises à jour
        last_status = video.get("status")
        last_ext = video.get("extensions_completed", 0)

        while True:
            # Attendre un message du client ou un timeout
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=3.0)
                if msg == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                pass

            # Vérifier les mises à jour Firestore
            current = firestore_service.get_video(video_id)
            if not current:
                break

            current_status = current.get("status")
            current_ext = current.get("extensions_completed", 0)

            if current_status != last_status or current_ext != last_ext:
                # Calculer progression
                ext_planned = current.get("extensions_planned", 0)
                if current_status == "completed":
                    progress = 100
                elif ext_planned > 0:
                    progress = int(((current_ext + 1) / (ext_planned + 1)) * 100)
                else:
                    progress = 50

                await websocket.send_json({
                    "type": "status",
                    "video_id": video_id,
                    "status": current_status,
                    "progress": progress,
                    "extensions_completed": current_ext,
                    "extensions_planned": ext_planned,
                })

                last_status = current_status
                last_ext = current_ext

                # Fin si terminé ou échoué
                if current_status in ("completed", "failed"):
                    if current_status == "completed":
                        from ..services.storage import storage_service_v3
                        stream_url = storage_service_v3.get_video_stream_url(video_id)
                        await websocket.send_json({
                            "type": "completed",
                            "video_id": video_id,
                            "stream_url": stream_url,
                        })
                    else:
                        await websocket.send_json({
                            "type": "failed",
                            "video_id": video_id,
                            "error": current.get("error", "Erreur inconnue"),
                        })
                    break

    except WebSocketDisconnect:
        logger.info(f"Client déconnecté: video={video_id}")
    finally:
        manager.disconnect(video_id, websocket)
