"""Modèles Pydantic pour les projets TikTok V3."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    theme: str = Field(default="custom", description="foot, manga, food, tech, custom...")
    description: Optional[str] = Field(None, max_length=500)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    theme: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)


class ProjectResponse(BaseModel):
    id: str
    name: str
    theme: str
    description: Optional[str] = None
    user_id: str
    character_count: int = 0
    video_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    count: int
