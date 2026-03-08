"""Router TikTok V3 — Suggestions IA pour profil, hashtags, titres."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from ..utils.jwt import get_current_user
from ..services.firestore_service import firestore_service
from ..services.tiktok_service import suggest_profile, suggest_hashtags, suggest_title

router = APIRouter(prefix="/api/v3/tiktok", tags=["tiktok"])


class ProfileSuggestRequest(BaseModel):
    project_id: str
    target_audience: Optional[str] = ""


class HashtagSuggestRequest(BaseModel):
    project_id: str
    video_description: Optional[str] = ""
    count: Optional[int] = 15


class TitleSuggestRequest(BaseModel):
    project_id: str
    video_description: Optional[str] = ""
    style: Optional[str] = "accrocheur"


@router.post("/suggest-profile")
async def get_profile_suggestion(
    data: ProfileSuggestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Suggère un profil TikTok optimisé pour le projet."""
    project = firestore_service.get_project(data.project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    result = await suggest_profile(
        theme=project.get("theme", project.get("name", "")),
        target_audience=data.target_audience,
    )
    return result


@router.post("/suggest-hashtags")
async def get_hashtag_suggestions(
    data: HashtagSuggestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Suggère des hashtags optimisés."""
    project = firestore_service.get_project(data.project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    result = await suggest_hashtags(
        theme=project.get("theme", project.get("name", "")),
        video_description=data.video_description,
        count=min(data.count, 30),  # Cap at 30
    )
    return result


@router.post("/suggest-title")
async def get_title_suggestions(
    data: TitleSuggestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Suggère des titres/légendes pour une vidéo."""
    project = firestore_service.get_project(data.project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    result = await suggest_title(
        theme=project.get("theme", project.get("name", "")),
        video_description=data.video_description,
        style=data.style,
    )
    return result
