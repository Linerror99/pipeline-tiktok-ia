from google.cloud import storage
from typing import List, Dict, Optional
from datetime import datetime, timedelta
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
    
    def get_video_url(self, video_id: str, expiration_minutes: int = 60) -> Optional[str]:
        """
        Génère une URL pour télécharger la vidéo
        
        Args:
            video_id: ID de la vidéo
            expiration_minutes: Durée de validité de l'URL en minutes (défaut: 60)
            
        Returns:
            URL ou None si la vidéo n'existe pas
        """
        try:
            blob_name = f"final_{video_id}.mp4"
            print(f"[get_video_url] Recherche du blob: {blob_name}")
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                print(f"[get_video_url] Blob {blob_name} n'existe pas")
                # Essayer de lister pour voir ce qui existe réellement
                print(f"[get_video_url] Fichiers commençant par 'final_': ")
                for b in self.bucket.list_blobs(prefix="final_", max_results=5):
                    print(f"  - {b.name}")
                return None
                
            # Essayer d'abord avec URL signée (nécessite service account)
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(minutes=expiration_minutes),
                    method="GET",
                    response_disposition=f'attachment; filename="video_{video_id}.mp4"'
                )
                return url
            except Exception as sign_error:
                print(f"Impossible de générer URL signée, utilisation URL publique: {sign_error}")
                # Fallback: rendre le blob public et retourner l'URL publique
                try:
                    blob.make_public()
                    return blob.public_url
                except Exception as public_error:
                    print(f"Impossible de rendre public: {public_error}")
                    # Dernier fallback: URL média Google Cloud Storage
                    return f"https://storage.googleapis.com/{self.bucket.name}/{blob.name}"
        except Exception as e:
            print(f"Erreur lors de la récupération de l'URL: {e}")
        
        return None
    
    def get_video_stream_url(self, video_id: str) -> Optional[str]:
        """
        Génère une URL pour streamer la vidéo (lecture dans le navigateur)
        
        Args:
            video_id: ID de la vidéo
            
        Returns:
            URL pour streaming ou None si la vidéo n'existe pas
        """
        try:
            blob_name = f"final_{video_id}.mp4"
            print(f"[get_video_stream_url] Recherche du blob: {blob_name}")
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                print(f"[get_video_stream_url] Blob {blob_name} n'existe pas")
                # Essayer de lister pour voir ce qui existe réellement
                print(f"[get_video_stream_url] Fichiers commençant par 'final_': ")
                for b in self.bucket.list_blobs(prefix="final_", max_results=5):
                    print(f"  - {b.name}")
                return None
            
            # Essayer d'abord avec URL signée (nécessite service account)
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(hours=2),
                    method="GET"
                )
                return url
            except Exception as sign_error:
                print(f"Impossible de générer URL signée, utilisation URL publique: {sign_error}")
                # Fallback: rendre le blob public et retourner l'URL publique
                try:
                    blob.make_public()
                    return blob.public_url
                except Exception as public_error:
                    print(f"Impossible de rendre public: {public_error}")
                    # Dernier fallback: URL média Google Cloud Storage
                    return f"https://storage.googleapis.com/{self.bucket.name}/{blob.name}"
        except Exception as e:
            print(f"Erreur lors de la génération de l'URL de streaming: {e}")
        
        return None
    
    def _extract_video_id(self, filename: str) -> str:
        """
        Extrait l'ID de la vidéo depuis le nom du fichier
        
        Le nom de fichier peut être de deux formats:
        - Ancien: final_YYYYMMDD_HHMMSS.mp4
        - Nouveau (avec thème): final_theme_slug.mp4
        """
        # Enlever "final_" et ".mp4"
        video_id = filename.replace('final_', '').replace('.mp4', '')
        return video_id
    
    def _get_theme_from_script(self, video_id: str) -> Optional[str]:
        """
        Extrait le titre depuis le fichier script
        
        Le script Gemini a ce format:
        Absolument. Voici un script détaillé...
        
        ### **Script Vidéo TikTok : [TITRE ICI]**
        
        Args:
            video_id: ID de la vidéo
            
        Returns:
            Le titre extrait ou None
        """
        try:
            script_blob = self.bucket.blob(f"script_{video_id}.txt")
            if not script_blob.exists():
                return None
            
            content = script_blob.download_as_text()
            
            # Pattern principal: ### **Script Vidéo TikTok : TITRE**
            pattern = r'###\s*\*\*Script\s+Vidéo\s+TikTok\s*:\s*([^*]+)\*\*'
            match = re.search(pattern, content, re.IGNORECASE)
            
            if match:
                title = match.group(1).strip()
                return title
            
            # Fallback 1: chercher juste après "###"
            pattern2 = r'###\s*\*\*([^*]+)\*\*'
            match2 = re.search(pattern2, content)
            
            if match2:
                title = match2.group(1).strip()
                # Enlever "Script Vidéo TikTok :" si présent au début
                title = re.sub(r'^Script\s+Vidéo\s+TikTok\s*:\s*', '', title, flags=re.IGNORECASE)
                return title
            
            # Fallback 2: prendre la première ligne significative (ancien comportement)
            lines = content.split('\n')
            for line in lines[:10]:
                if line.strip() and not line.startswith('SCÈNE') and not line.startswith('**SCÈNE'):
                    return line.strip()[:100]
                    
        except Exception as e:
            print(f"Erreur lors de la lecture du script: {e}")
        
        return None


storage_service = StorageService()
