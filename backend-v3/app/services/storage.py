"""Service Storage V3 — Gestion des fichiers dans Cloud Storage V3."""
from google.cloud import storage
from typing import Optional, List
from datetime import timedelta
import uuid

from ..config import settings


class StorageServiceV3:
    """Interagit avec les buckets V3 (videos, uploads, thumbnails)."""

    def __init__(self):
        self.client = storage.Client(project=settings.PROJECT_ID)
        self.videos_bucket = self.client.bucket(settings.BUCKET_NAME_V3)
        self.uploads_bucket = self.client.bucket(settings.BUCKET_UPLOADS_V3)
        self.thumbnails_bucket = self.client.bucket(settings.BUCKET_THUMBNAILS_V3)

    # ── Upload fichiers utilisateur ─────────────────────────

    def upload_file(self, project_id: str, file_bytes: bytes, filename: str, content_type: str) -> dict:
        """Upload un fichier dans le bucket uploads V3."""
        file_id = uuid.uuid4().hex[:12]
        blob_name = f"{project_id}/{file_id}_{filename}"
        blob = self.uploads_bucket.blob(blob_name)
        blob.upload_from_string(file_bytes, content_type=content_type)
        return {
            "file_id": file_id,
            "filename": filename,
            "gcs_uri": f"gs://{settings.BUCKET_UPLOADS_V3}/{blob_name}",
            "content_type": content_type,
            "size": len(file_bytes),
        }

    def get_upload_url(self, gcs_uri: str, expiration_minutes: int = 60) -> Optional[str]:
        """Génère une URL signée pour un fichier uploadé."""
        if not gcs_uri.startswith("gs://"):
            return None
        parts = gcs_uri[5:].split("/", 1)
        bucket = self.client.bucket(parts[0])
        blob = bucket.blob(parts[1])
        try:
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
            )
        except Exception:
            return f"https://storage.googleapis.com/{parts[0]}/{parts[1]}"

    # ── Script V3 (déclenche agent-video-veo31) ─────────────

    def upload_script_v3(self, video_id: str, script_data: dict) -> str:
        """Upload script_v3.json dans le bucket V3 → déclenche la Cloud Function."""
        import json
        blob_name = f"{video_id}/script_v3.json"
        blob = self.videos_bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(script_data), content_type="application/json")
        return f"gs://{settings.BUCKET_NAME_V3}/{blob_name}"

    # ── Vidéos finales ──────────────────────────────────────

    def get_video_stream_url(self, video_id: str, expiration_hours: int = 2) -> Optional[str]:
        """URL signée pour streamer une vidéo V3."""
        blob = self.videos_bucket.blob(f"{video_id}/final.mp4")
        if not blob.exists():
            return None
        try:
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=expiration_hours),
                method="GET",
            )
        except Exception:
            return f"https://storage.googleapis.com/{settings.BUCKET_NAME_V3}/{video_id}/final.mp4"

    def get_video_download_url(self, video_id: str, expiration_minutes: int = 60) -> Optional[str]:
        """URL signée pour télécharger une vidéo V3."""
        blob = self.videos_bucket.blob(f"{video_id}/final.mp4")
        if not blob.exists():
            return None
        try:
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
                response_disposition=f'attachment; filename="{video_id}.mp4"',
            )
        except Exception:
            return None

    # ── Thumbnails ──────────────────────────────────────────

    def get_thumbnail_url(self, video_id: str) -> Optional[str]:
        """URL publique ou signée de la thumbnail."""
        blob = self.thumbnails_bucket.blob(f"{video_id}/thumbnail.png")
        if not blob.exists():
            return None
        try:
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=24),
                method="GET",
            )
        except Exception:
            return None

    # ── Character images ────────────────────────────────────

    def upload_character_image(self, character_id: str, image_bytes: bytes, index: int = 0) -> str:
        """Upload une image de personnage générée par Imagen 4."""
        blob_name = f"characters/{character_id}/image_{index}.png"
        blob = self.uploads_bucket.blob(blob_name)
        blob.upload_from_string(image_bytes, content_type="image/png")
        return f"gs://{settings.BUCKET_UPLOADS_V3}/{blob_name}"

    def get_character_image_url(self, gcs_uri: str) -> Optional[str]:
        """URL signée pour une image de personnage."""
        return self.get_upload_url(gcs_uri)


storage_service_v3 = StorageServiceV3()
