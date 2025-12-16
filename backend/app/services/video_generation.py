import requests
from typing import Dict
from datetime import datetime
from ..config import settings


class VideoGenerationService:
    """Service pour déclencher la génération de vidéos"""
    
    def __init__(self):
        self.script_agent_url = settings.SCRIPT_AGENT_URL
    
    def create_video(self, theme: str) -> Dict:
        """
        Déclenche la génération d'une vidéo en appelant l'agent script
        
        Args:
            theme: Le thème de la vidéo à générer
            
        Returns:
            Dict avec video_id et status
        """
        if not self.script_agent_url:
            raise ValueError(
                "SCRIPT_AGENT_URL n'est pas configurée. "
                "Veuillez définir l'URL de votre Cloud Function dans .env"
            )
        
        # Générer un ID unique pour la vidéo
        video_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Appeler la Cloud Function agent-script
            response = requests.post(
                self.script_agent_url,
                json={"theme": theme},
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minutes timeout
            )
            
            response.raise_for_status()
            
            return {
                "video_id": video_id,
                "status": "processing",
                "message": "Génération de la vidéo démarrée avec succès",
                "theme": theme
            }
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'appel à l'agent script: {str(e)}")


video_generation_service = VideoGenerationService()
