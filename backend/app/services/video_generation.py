import requests
from typing import Dict, Optional
from datetime import datetime
from ..config import settings


class VideoGenerationService:
    """Service pour déclencher la génération de vidéos V2 (Veo 3.1)"""
    
    def __init__(self):
        self.script_agent_url = settings.SCRIPT_AGENT_URL
    
    def create_video(
        self, 
        theme: str, 
        target_duration: int = 36,
        style: str = "informative",
        language: str = "fr"
    ) -> Dict:
        """
        Déclenche la génération d'une vidéo V2 en appelant agent-script-v2
        
        Args:
            theme: Le thème de la vidéo à générer
            target_duration: Durée cible en secondes (8-78s)
            style: Style visuel (informative, humorous, dramatic, inspiring)
            language: Langue (fr, en, es)
            
        Returns:
            Dict avec video_id, status, blocks_generated, duration
        """
        if not self.script_agent_url:
            raise ValueError(
                "SCRIPT_AGENT_URL n'est pas configurée. "
                "Veuillez définir l'URL de agent-script-v2 dans .env"
            )
        
        # Générer un ID unique pour la vidéo
        video_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Appeler agent-script-v2
            payload = {
                "theme": theme,
                "video_id": video_id,
                "target_duration": target_duration,
                "style": style,
                "language": language
            }
            
            response = requests.post(
                self.script_agent_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # 1 minute timeout pour génération script
            )
            
            response.raise_for_status()
            result = response.json()
            
            # agent-script-v2 renvoie: {status, video_id, blocks_generated, duration, message}
            return {
                "video_id": result.get("video_id", video_id),
                "status": "script_generated",
                "message": result.get("message", "Génération démarrée"),
                "theme": theme,
                "blocks_generated": result.get("blocks_generated", 0),
                "duration": result.get("duration", target_duration)
            }
        
        except requests.exceptions.Timeout:
            raise Exception("Timeout lors de la génération du script (>60s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'appel à agent-script-v2: {str(e)}")


video_generation_service = VideoGenerationService()
