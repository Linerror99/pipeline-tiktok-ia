from google.cloud import storage, firestore
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from ..config import settings


class StorageService:
    """Service pour interagir avec Google Cloud Storage et Firestore V2"""
    
    def __init__(self):
        self.storage_client = storage.Client(project=settings.PROJECT_ID)
        self.firestore_client = firestore.Client(project=settings.PROJECT_ID)
        self.bucket = self.storage_client.bucket(settings.BUCKET_NAME_V2)
    
    def list_videos(self) -> List[Dict]:
        """Liste toutes les vidéos depuis Firestore v2_veo_operations"""
        videos = []
        
        try:
            # Récupérer depuis Firestore v2_veo_operations
            docs = self.firestore_client.collection('v2_veo_operations').stream()
            
            for doc in docs:
                data = doc.to_dict()
                
                # Ignorer les vidéos sans statut ou non complétées
                if not data or data.get('status') not in ['completed', 'ready_for_assembly', 'generating_parallel', 'failed']:
                    continue
                
                # Générer URL signée pour vidéos complétées
                stream_url = None
                if data.get('status') == 'completed' and data.get('final_url'):
                    # Vérifier si final_url est un path GCS (gs://) ou déjà une URL HTTP
                    final_url_value = data.get('final_url')
                    if final_url_value.startswith('gs://'):
                        # Générer URL signée depuis le path GCS
                        stream_url = self.get_video_stream_url(doc.id)
                    else:
                        # Déjà une URL HTTP
                        stream_url = final_url_value
                
                video_info = {
                    "id": doc.id,
                    "video_id": doc.id,  # Alias pour compatibilité frontend
                    "theme": self._extract_theme_from_blocks(data.get('blocks', [])),
                    "status": self._map_status(data.get('status')),
                    "created_at": data.get('created_at').isoformat() if data.get('created_at') else None,
                    "video_url": stream_url,  # URL signée HTTP
                    "stream_url": stream_url,  # Alias pour compatibilité
                    "thumbnail_url": None,  # TODO: Générer thumbnails
                    "duration": self._calculate_duration(data.get('total_blocks', 0)),
                    "blocks_count": data.get('total_blocks', 0),
                    "completed_blocks": data.get('completed_blocks', 0),
                }
                videos.append(video_info)
            
            # Trier par date de création (plus récent en premier)
            videos.sort(key=lambda x: x['created_at'] or '', reverse=True)
            
        except Exception as e:
            print(f"Erreur lors de la récupération des vidéos: {e}")
        
        return videos
    
    def get_video_status(self, video_id: str) -> Dict:
        """Récupère le statut d'une vidéo depuis Firestore v2_video_status"""
        try:
            # Récupérer depuis v2_video_status
            doc = self.firestore_client.collection('v2_video_status').document(video_id).get()
            
            if not doc.exists:
                # Fallback: chercher dans v2_veo_operations
                op_doc = self.firestore_client.collection('v2_veo_operations').document(video_id).get()
                if op_doc.exists:
                    data = op_doc.to_dict()
                    return self._build_status_from_operations(video_id, data)
                
                return {
                    "video_id": video_id,
                    "status": "not_found",
                    "error": "Vidéo non trouvée"
                }
            
            data = doc.to_dict()
            status_info = {
                "video_id": video_id,
                "status": data.get('status', 'unknown'),
                "current_step": data.get('current_step'),
                "progress": self._calculate_progress(data),
                "error_message": data.get('error_message'),
                "created_at": data.get('created_at').isoformat() if data.get('created_at') else None,
                "updated_at": data.get('updated_at').isoformat() if data.get('updated_at') else None,
            }
            
            # Si complété, ajouter l'URL
            if data.get('status') == 'completed':
                op_doc = self.firestore_client.collection('v2_veo_operations').document(video_id).get()
                if op_doc.exists:
                    op_data = op_doc.to_dict()
                    status_info['final_url'] = op_data.get('final_url')
                    status_info['total_blocks'] = op_data.get('total_blocks', 0)
                    status_info['completed_blocks'] = op_data.get('completed_blocks', 0)
            
            return status_info
        
        except Exception as e:
            print(f"Erreur lors de la récupération du statut: {e}")
            return {
                "video_id": video_id,
                "status": "error",
                "error": str(e)
            }
    
    def _build_status_from_operations(self, video_id: str, data: Dict) -> Dict:
        """Construit le statut depuis v2_veo_operations"""
        status = data.get('status', 'unknown')
        total_blocks = data.get('total_blocks', 0)
        completed_blocks = data.get('completed_blocks', 0)
        
        return {
            "video_id": video_id,
            "status": status,
            "current_step": self._get_current_step(status, completed_blocks, total_blocks),
            "total_blocks": total_blocks,
            "completed_blocks": completed_blocks,
            "progress": int((completed_blocks / total_blocks * 100) if total_blocks > 0 else 0),
            "final_url": data.get('final_url'),
            "created_at": data.get('created_at').isoformat() if data.get('created_at') else None,
            "updated_at": data.get('updated_at').isoformat() if data.get('updated_at') else None,
        }
    
    def _map_status(self, firestore_status: str) -> str:
        """Mappe les status Firestore vers status API"""
        status_map = {
            'script_generated': 'processing',
            'generating_parallel': 'processing',
            'ready_for_assembly': 'processing',
            'completed': 'completed',
            'failed': 'failed',
            'error': 'failed'
        }
        return status_map.get(firestore_status, 'processing')
    
    def _get_current_step(self, status: str, completed: int, total: int) -> str:
        """Génère message d'étape actuelle"""
        if status == 'script_generated':
            return "Script généré, lancement génération vidéos..."
        elif status == 'generating_parallel':
            return f"Génération vidéos ({completed}/{total} blocs)"
        elif status == 'ready_for_assembly':
            return "Assemblage en cours..."
        elif status == 'completed':
            return "Vidéo terminée"
        elif status == 'failed' or status == 'error':
            return "Erreur lors de la génération"
        return "En cours..."
    
    def _calculate_progress(self, data: Dict) -> int:
        """Calcule le pourcentage de progression"""
        status = data.get('status')
        
        if status == 'completed':
            return 100
        elif status == 'failed' or status == 'error':
            return 0
        elif status == 'script_generated':
            return 10
        
        # Pour génération parallèle, estimer sur base des blocs
        total_blocks = data.get('total_blocks', 0)
        completed_blocks = data.get('completed_blocks', 0)
        
        if total_blocks > 0:
            # 10% pour script, 80% pour génération, 10% pour assemblage
            block_progress = int((completed_blocks / total_blocks) * 80)
            return 10 + block_progress
        
        return 20  # Défaut
    
    def _extract_theme_from_blocks(self, blocks: List[Dict]) -> str:
        """Extrait un thème descriptif depuis les blocs"""
        if not blocks:
            return "Vidéo sans titre"
        
        # Prendre le dialogue du premier bloc
        first_dialogue = blocks[0].get('dialogue', '') if blocks else ''
        if len(first_dialogue) > 50:
            return first_dialogue[:50] + "..."
        return first_dialogue or "Vidéo sans titre"
    
    def _calculate_duration(self, total_blocks: int) -> int:
        """Calcule la durée totale en secondes"""
        if total_blocks == 0:
            return 0
        elif total_blocks == 1:
            return 8
        else:
            return 8 + (total_blocks - 1) * 7
    
    def get_video_url(self, video_id: str, expiration_minutes: int = 60) -> Optional[str]:
        """
        Génère une URL pour télécharger la vidéo V2
        
        Args:
            video_id: ID de la vidéo
            expiration_minutes: Durée de validité de l'URL en minutes (défaut: 60)
            
        Returns:
            URL ou None si la vidéo n'existe pas
        """
        try:
            # Format V2: {video_id}/final.mp4
            blob_name = f"{video_id}/final.mp4"
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                print(f"[get_video_url] Vidéo V2 non trouvée: {blob_name}")
                return None
                
            # Générer URL signée
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(minutes=expiration_minutes),
                    method="GET",
                    response_disposition=f'attachment; filename="{video_id}.mp4"'
                )
                return url
            except Exception as sign_error:
                print(f"Impossible de générer URL signée: {sign_error}")
                # Fallback: URL publique
                return f"https://storage.googleapis.com/{self.bucket.name}/{blob_name}"
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
            # Format V2: {video_id}/final.mp4
            blob_name = f"{video_id}/final.mp4"
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
