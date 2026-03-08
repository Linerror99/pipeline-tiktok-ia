"""Modèles Pydantic pour les vidéos V3 (Veo 3.1 extensions)."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Paliers Veo 3.1 : 8 + N×7
VALID_DURATIONS = [8, 15, 22, 29, 36, 43, 50, 57]


class VideoGenerateRequest(BaseModel):
    """Lancer la génération vidéo depuis un scénario validé."""
    scenario_id: str
    project_id: str


class VideoResponse(BaseModel):
    id: str
    project_id: str
    scenario_id: str
    status: str = "pending"  # pending, generating, extending_N, completed, failed
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    target_duration: int = 22
    actual_duration: Optional[int] = None
    has_native_audio: bool = True
    extensions_planned: int = 0
    extensions_completed: int = 0
    tiktok_title: Optional[str] = None
    tiktok_hashtags: List[str] = []
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class VideoStatusResponse(BaseModel):
    video_id: str
    status: str
    progress: int = 0  # 0-100
    current_step: str = "En attente..."
    extensions_completed: int = 0
    extensions_total: int = 0
    error: Optional[str] = None


class VideoListResponse(BaseModel):
    videos: List[VideoResponse]
    count: int
