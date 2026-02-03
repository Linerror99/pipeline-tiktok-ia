from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from google.cloud import firestore
from typing import Dict, Set
import asyncio
import json
from ..config import settings
from ..utils.jwt import decode_token

router = APIRouter(prefix="/ws", tags=["websocket"])

# Gestionnaire de connexions WebSocket
class ConnectionManager:
    def __init__(self):
        # Dict[video_id, Set[WebSocket]]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.firestore_client = firestore.Client(project=settings.PROJECT_ID)
        self.watchers: Dict[str, any] = {}  # Firestore watchers
    
    async def connect(self, websocket: WebSocket, video_id: str):
        """Connecte un client WebSocket"""
        await websocket.accept()
        
        if video_id not in self.active_connections:
            self.active_connections[video_id] = set()
        
        self.active_connections[video_id].add(websocket)
        print(f"[WebSocket] Client connecté pour video {video_id}. Total: {len(self.active_connections[video_id])}")
        
        # Démarrer le watcher Firestore si premier client
        if len(self.active_connections[video_id]) == 1:
            await self.start_firestore_watcher(video_id)
        
        # Envoyer le statut initial
        await self.send_initial_status(websocket, video_id)
    
    def disconnect(self, websocket: WebSocket, video_id: str):
        """Déconnecte un client WebSocket"""
        if video_id in self.active_connections:
            self.active_connections[video_id].discard(websocket)
            print(f"[WebSocket] Client déconnecté pour video {video_id}. Restant: {len(self.active_connections[video_id])}")
            
            # Arrêter le watcher si plus de clients
            if len(self.active_connections[video_id]) == 0:
                self.stop_firestore_watcher(video_id)
                del self.active_connections[video_id]
    
    async def send_initial_status(self, websocket: WebSocket, video_id: str):
        """Envoie le statut initial au client"""
        try:
            doc = self.firestore_client.collection('v2_video_status').document(video_id).get()
            if doc.exists:
                data = doc.to_dict()
                await websocket.send_json(self._format_status(video_id, data))
        except Exception as e:
            print(f"[WebSocket] Erreur envoi statut initial: {e}")
    
    async def start_firestore_watcher(self, video_id: str):
        """Démarre le watcher Firestore pour un video_id"""
        try:
            doc_ref = self.firestore_client.collection('v2_video_status').document(video_id)
            
            def on_snapshot(doc_snapshot, changes, read_time):
                """Callback quand le document change"""
                for doc in doc_snapshot:
                    if doc.exists:
                        data = doc.to_dict()
                        asyncio.create_task(self.broadcast_to_video(video_id, data))
            
            # Créer le watcher
            watcher = doc_ref.on_snapshot(on_snapshot)
            self.watchers[video_id] = watcher
            print(f"[WebSocket] Watcher Firestore démarré pour {video_id}")
            
        except Exception as e:
            print(f"[WebSocket] Erreur création watcher: {e}")
    
    def stop_firestore_watcher(self, video_id: str):
        """Arrête le watcher Firestore"""
        if video_id in self.watchers:
            self.watchers[video_id].unsubscribe()
            del self.watchers[video_id]
            print(f"[WebSocket] Watcher Firestore arrêté pour {video_id}")
    
    async def broadcast_to_video(self, video_id: str, data: Dict):
        """Broadcast le statut à tous les clients d'une vidéo"""
        if video_id not in self.active_connections:
            return
        
        message = self._format_status(video_id, data)
        disconnected = set()
        
        for websocket in self.active_connections[video_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"[WebSocket] Erreur envoi message: {e}")
                disconnected.add(websocket)
        
        # Nettoyer les connexions mortes
        for websocket in disconnected:
            self.active_connections[video_id].discard(websocket)
    
    def _format_status(self, video_id: str, data: Dict) -> Dict:
        """Formate les données Firestore pour le frontend"""
        status = data.get('status', 'unknown')
        
        # Récupérer infos supplémentaires depuis v2_veo_operations si besoin
        total_blocks = data.get('total_blocks', 0)
        completed_blocks = data.get('completed_blocks', 0)
        
        if not total_blocks and status in ['generating_parallel', 'ready_for_assembly', 'completed']:
            try:
                op_doc = self.firestore_client.collection('v2_veo_operations').document(video_id).get()
                if op_doc.exists:
                    op_data = op_doc.to_dict()
                    total_blocks = op_data.get('total_blocks', 0)
                    
                    # Calculer completed_blocks depuis clips_status
                    clips_status = op_data.get('clips_status', {})
                    if clips_status:
                        completed_blocks = sum(1 for status_val in clips_status.values() if status_val == 'completed')
                    else:
                        completed_blocks = op_data.get('completed_blocks', 0)
            except:
                pass
        
        return {
            "video_id": video_id,
            "status": status,
            "current_step": data.get('current_step') or self._get_step_message(status, completed_blocks, total_blocks),
            "total_blocks": total_blocks,
            "completed_blocks": completed_blocks,
            "progress": self._calculate_progress(status, completed_blocks, total_blocks),
            "error_message": data.get('error_message'),
            "updated_at": data.get('updated_at').isoformat() if data.get('updated_at') else None,
        }
    
    def _get_step_message(self, status: str, completed: int, total: int) -> str:
        """Génère message d'étape"""
        if status == 'script_generated':
            return "Script généré, lancement génération..."
        elif status == 'generating_parallel':
            return f"Génération vidéos ({completed}/{total} blocs)"
        elif status == 'ready_for_assembly':
            return "Assemblage en cours..."
        elif status == 'completed':
            return "Vidéo terminée !"
        elif status == 'failed' or status == 'error':
            return "Erreur lors de la génération"
        return "En cours..."
    
    def _calculate_progress(self, status: str, completed: int, total: int) -> int:
        """Calcule progression en %"""
        if status == 'completed':
            return 100
        elif status == 'failed' or status == 'error':
            return 0
        elif status == 'script_generated':
            return 10
        elif status == 'generating_parallel' and total > 0:
            return 10 + int((completed / total) * 80)
        elif status == 'ready_for_assembly':
            return 95
        return 20


# Instance globale du manager
manager = ConnectionManager()


@router.websocket("/video/{video_id}")
async def websocket_video_status(
    websocket: WebSocket,
    video_id: str,
    token: str = Query(None, description="JWT token pour authentification (optionnel pour tests)")
):
    """
    WebSocket endpoint pour suivre le statut d'une vidéo en temps réel
    
    Usage:
    ws://backend-url/ws/video/{video_id}?token={jwt_token}
    """
    # Authentification optionnelle pour les tests
    if token:
        try:
            payload = decode_token(token)
            if not payload:
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception as e:
            print(f"[WebSocket] Erreur authentification: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    # Connexion
    await manager.connect(websocket, video_id)
    
    try:
        # Garder la connexion ouverte
        while True:
            # Recevoir messages du client (ping/pong)
            data = await websocket.receive_text()
            
            # Le client peut envoyer "ping" pour garder la connexion
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, video_id)
    except Exception as e:
        print(f"[WebSocket] Erreur: {e}")
        manager.disconnect(websocket, video_id)
