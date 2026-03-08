"""Modèles Pydantic pour les personnages V3 (Imagen 4)."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CharacterChatRequest(BaseModel):
    """Message dans le chat de création de personnage."""
    project_id: str
    message: str = Field(..., min_length=1, max_length=2000)
    character_id: Optional[str] = None  # Si continuation d'un chat existant


class CharacterChatResponse(BaseModel):
    ai_message: str
    character_id: str
    suggested_traits: Optional[dict] = None  # nom, style, couleurs, etc.
    ready_to_generate: bool = False


class CharacterGenerateRequest(BaseModel):
    """Demande de génération d'image Imagen 4."""
    character_id: str
    project_id: str


class CharacterResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    traits: Optional[dict] = None
    image_url: Optional[str] = None
    reference_images: List[str] = []
    chat_history: List[dict] = []
    status: str = "draft"  # draft, generating, ready
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CharacterListResponse(BaseModel):
    characters: List[CharacterResponse]
    count: int
