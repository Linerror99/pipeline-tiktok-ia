"""Modèles Pydantic pour les scénarios V3 (Chat IA + fichiers)."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ScenarioChatRequest(BaseModel):
    """Message dans le chat de création de scénario."""
    project_id: str
    message: str = Field(..., min_length=1, max_length=5000)
    scenario_id: Optional[str] = None
    # IDs des fichiers uploadés à inclure dans le contexte
    file_ids: List[str] = []


class ScenarioChatResponse(BaseModel):
    ai_message: str
    scenario_id: str
    script_preview: Optional[dict] = None  # blocs VISUEL + DIALOGUE
    ready_to_validate: bool = False


class ScenarioValidateRequest(BaseModel):
    """Validation du scénario pour lancer la génération."""
    scenario_id: str
    project_id: str
    target_duration: int = Field(default=22, ge=8, le=57)
    character_ids: List[str] = []


class ScenarioResponse(BaseModel):
    id: str
    project_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    script: Optional[dict] = None  # {blocks: [...], target_duration: int}
    uploaded_files: List[dict] = []
    chat_history: List[dict] = []
    character_ids: List[str] = []
    status: str = "draft"  # draft, validated, generating, completed
    target_duration: int = 22
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioResponse]
    count: int
