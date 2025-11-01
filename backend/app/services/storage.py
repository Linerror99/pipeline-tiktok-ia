from google.cloud import storage
from typing import List, Dict, Optional
from datetime import datetime
import re
from ..config import settings


class StorageService:
    """Service pour interagir avec Google Cloud Storage"""
    
    def __init__(self):
        self.client = storage.Client(project=settings.PROJECT_ID)
        self.bucket = self.client.bucket(settings.BUCKET_NAME)
    
    def list_videos(self) -> List[Dict]:
        """Liste toutes les vidéos finales générées"""
        videos = []
        
        try:
            # Récupérer tous les fichiers final_*.mp4
            blobs = self.bucket.list_blobs(prefix="final_")
            
            for blob in blobs:
                if blob.name.endswith('.mp4'):
                    # Extraire l'ID de la vidéo depuis le nom du fichier
                    video_id = self._extract_video_id(blob.name)
                    
                    # Récupérer le script associé pour avoir le thème
                    theme = self._get_theme_from_script(video_id)
                    
                    video_info = {
                        "id": video_id,
                        "theme": theme or "Thème inconnu",
                        "status": "completed",
                        "created_at": blob.time_created.isoformat() if blob.time_created else None,
                        "video_url": blob.public_url,
                        "thumbnail_url": None,  # TODO: Générer des thumbnails
                        "duration": None,  # TODO: Extraire la durée de la vidéo
                    }
                    videos.append(video_info)
            
            # Trier par date de création (plus récent en premier)
            videos.sort(key=lambda x: x['created_at'] or '', reverse=True)
            
        except Exception as e:
            print(f"Erreur lors de la récupération des vidéos: {e}")
        
        return videos
    
    def get_video_status(self, video_id: str) -> Dict:
        """Récupère le statut d'une vidéo en cours de génération"""
        status = {
            "video_id": video_id,
            "stage": "unknown",
            "status": "processing",
            "files": {}
        }
        
        try:
            # Vérifier l'existence des fichiers à chaque étape
            script_blob = self.bucket.blob(f"script_{video_id}.txt")
            audio_blob = self.bucket.blob(f"audio_{video_id}.mp3")
            video_folder_prefix = f"video_clips/{video_id}/"
            final_blob = self.bucket.blob(f"final_{video_id}.mp4")
            
            if final_blob.exists():
                status["stage"] = "completed"
                status["status"] = "completed"
                status["files"]["final"] = final_blob.public_url
            elif list(self.bucket.list_blobs(prefix=video_folder_prefix, max_results=1)):
                status["stage"] = "assembling"
                status["status"] = "processing"
            elif audio_blob.exists():
                status["stage"] = "generating_video"
                status["status"] = "processing"
                status["files"]["audio"] = audio_blob.public_url
            elif script_blob.exists():
                status["stage"] = "generating_audio"
                status["status"] = "processing"
                status["files"]["script"] = script_blob.public_url
            else:
                status["stage"] = "generating_script"
                status["status"] = "processing"
        
        except Exception as e:
            print(f"Erreur lors de la vérification du statut: {e}")
            status["status"] = "error"
            status["error"] = str(e)
        
        return status
    
    def get_video_url(self, video_id: str) -> Optional[str]:
        """Récupère l'URL de téléchargement d'une vidéo"""
        try:
            blob = self.bucket.blob(f"final_{video_id}.mp4")
            if blob.exists():
                # Générer une URL signée valide 1 heure
                return blob.generate_signed_url(expiration=3600)
        except Exception as e:
            print(f"Erreur lors de la récupération de l'URL: {e}")
        
        return None
    
    def _extract_video_id(self, filename: str) -> str:
        """Extrait l'ID de la vidéo depuis le nom du fichier"""
        # Format: final_YYYYMMDD_HHMMSS.mp4
        match = re.search(r'final_(\d+_\d+)', filename)
        if match:
            return match.group(1)
        return filename.replace('final_', '').replace('.mp4', '')
    
    def _get_theme_from_script(self, video_id: str) -> Optional[str]:
        """Récupère le thème depuis le fichier script"""
        try:
            script_blob = self.bucket.blob(f"script_{video_id}.txt")
            if script_blob.exists():
                content = script_blob.download_as_text()
                # Le thème est généralement dans les premières lignes
                lines = content.split('\n')
                for line in lines[:5]:
                    if line.strip() and not line.startswith('SCÈNE'):
                        return line.strip()[:100]  # Limiter à 100 caractères
        except Exception as e:
            print(f"Erreur lors de la lecture du script: {e}")
        
        return None


storage_service = StorageService()
