"""Service TikTok V3 — Suggestions IA pour profil, hashtags, titres."""
from google import genai
from google.genai import types
from typing import List, Optional
import json
import re

from ..config import settings

GEMINI_MODEL = "gemini-3.1-pro-preview"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=settings.PROJECT_ID,
            location=settings.REGION,
        )
    return _client


async def suggest_profile(theme: str, target_audience: str = "") -> dict:
    """Suggère un profil TikTok optimisé pour le thème du projet."""
    client = _get_client()
    prompt = f"""Tu es un expert TikTok/Shorts. Suggère un profil TikTok optimisé.

Thème du projet : {theme}
{"Public cible : " + target_audience if target_audience else ""}

Réponds UNIQUEMENT en JSON valide :
{{
  "username": "suggestion de @username",
  "display_name": "Nom d'affichage",
  "bio": "Bio de 80 caractères max",
  "niche_tags": ["tag1", "tag2", "tag3"],
  "posting_frequency": "Fréquence recommandée",
  "best_posting_times": ["horaire1", "horaire2"]
}}"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=500,
        ),
    )

    return _parse_json_response(response.text, fallback_key="profile")


async def suggest_hashtags(
    theme: str,
    video_description: str = "",
    count: int = 15,
) -> dict:
    """Suggère des hashtags optimisés pour une vidéo TikTok."""
    client = _get_client()
    prompt = f"""Tu es un expert TikTok/Shorts. Suggère {count} hashtags optimisés.

Thème : {theme}
{"Description vidéo : " + video_description if video_description else ""}

Réponds UNIQUEMENT en JSON valide :
{{
  "hashtags": ["#hashtag1", "#hashtag2", ...],
  "primary": ["#top3hashtag1", "#top3hashtag2", "#top3hashtag3"],
  "trending": ["hashtags tendance actuels"],
  "niche": ["hashtags de niche"]
}}"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            temperature=0.6,
            max_output_tokens=500,
        ),
    )

    return _parse_json_response(response.text, fallback_key="hashtags")


async def suggest_title(
    theme: str,
    video_description: str = "",
    style: str = "accrocheur",
) -> dict:
    """Suggère des titres/légendes pour une vidéo TikTok."""
    client = _get_client()
    prompt = f"""Tu es un expert TikTok/Shorts. Suggère 5 titres/légendes pour une vidéo.

Thème : {theme}
{"Description : " + video_description if video_description else ""}
Style souhaité : {style}

Réponds UNIQUEMENT en JSON valide :
{{
  "titles": [
    {{"title": "Titre 1", "hook_type": "question|choc|emotion|curiosité"}},
    {{"title": "Titre 2", "hook_type": "..."}},
    ...
  ],
  "recommended": "Le meilleur titre",
  "caption_tip": "Conseil pour la légende"
}}"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=600,
        ),
    )

    return _parse_json_response(response.text, fallback_key="titles")


def _parse_json_response(text: str, fallback_key: str = "data") -> dict:
    """Parse une réponse JSON de Gemini, avec fallback."""
    # Tenter le bloc ```json
    match = re.search(r"```json\s*\n(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Tenter le JSON brut { ... }
    match2 = re.search(r"\{.*\}", text, re.DOTALL)
    if match2:
        try:
            return json.loads(match2.group(0))
        except json.JSONDecodeError:
            pass

    # Fallback : retourner le texte brut
    return {fallback_key: text}
