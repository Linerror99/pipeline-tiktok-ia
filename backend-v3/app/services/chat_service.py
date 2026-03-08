"""Service Chat IA V3 — Gemini 3.1 Pro pour personnages et scénarios."""
from google import genai
from google.genai import types
from typing import List, Optional
import json

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


# ── Chat Personnages ────────────────────────────────────

CHARACTER_SYSTEM_PROMPT = """Tu es un assistant créatif spécialisé dans la création de personnages animés pour TikTok.
Tu aides l'utilisateur à définir un personnage unique avec :
- Un nom accrocheur
- Un style visuel (cartoon, anime, 3D, pixel art...)
- Des couleurs dominantes
- Une personnalité (drôle, sérieux, mystérieux...)
- Un look distinctif (vêtements, accessoires)

Pose des questions pour affiner le personnage. Quand tu as assez d'informations,
propose un résumé structuré et indique que le personnage est prêt à être généré.

Réponds toujours en français. Sois concis et créatif."""


def chat_character(chat_history: List[dict], user_message: str, project_theme: str = "") -> dict:
    """Chat avec Gemini pour créer/affiner un personnage."""
    client = _get_client()

    messages = [{"role": "user", "parts": [{"text": CHARACTER_SYSTEM_PROMPT}]}]
    if project_theme:
        messages.append({
            "role": "user",
            "parts": [{"text": f"Le projet est sur le thème : {project_theme}"}],
        })
        messages.append({
            "role": "model",
            "parts": [{"text": "Super ! Créons un personnage pour ce thème. Quel genre de personnage imagines-tu ?"}],
        })

    # Historique existant
    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "parts": [{"text": msg["content"]}],
        })

    # Nouveau message
    messages.append({"role": "user", "parts": [{"text": user_message}]})

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=messages,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=1000,
        ),
    )

    ai_text = response.text

    # Détecter si le personnage est prêt
    ready_keywords = ["prêt à être généré", "prêt pour la génération", "on peut le générer", "je peux le générer"]
    ready = any(kw in ai_text.lower() for kw in ready_keywords)

    # Extraire traits si mentionnés
    traits = _extract_character_traits(ai_text)

    return {
        "ai_message": ai_text,
        "ready_to_generate": ready,
        "suggested_traits": traits,
    }


def _extract_character_traits(text: str) -> Optional[dict]:
    """Tente d'extraire les traits du personnage depuis la réponse IA."""
    # Heuristique simple : chercher des patterns structurés
    traits = {}
    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower().strip()
        if "nom" in line_lower and ":" in line:
            traits["name"] = line.split(":", 1)[1].strip().strip("*").strip()
        elif "style" in line_lower and ":" in line:
            traits["style"] = line.split(":", 1)[1].strip().strip("*").strip()
        elif "couleur" in line_lower and ":" in line:
            traits["colors"] = line.split(":", 1)[1].strip().strip("*").strip()
        elif "personnalité" in line_lower and ":" in line:
            traits["personality"] = line.split(":", 1)[1].strip().strip("*").strip()
    return traits if traits else None


# ── Chat Scénarios ──────────────────────────────────────

SCENARIO_SYSTEM_PROMPT = """Tu es un scénariste professionnel pour vidéos TikTok/Shorts.
Tu aides l'utilisateur à écrire un scénario avec :
- Des blocs VISUEL (description de la scène pour Veo 3.1)
- Des blocs DIALOGUE (texte parlé par les personnages, généré en audio par Veo)

Chaque bloc = ~7 secondes de vidéo. Le premier bloc = 8 secondes.
L'audio est natif (généré par Veo, pas de TTS externe).

Si l'utilisateur upload des fichiers (images, documents), analyse-les et intègre le contexte.

Quand le scénario est complet, génère le script final au format JSON :
```json
{
  "blocks": [
    {"visuel": "Description visuelle...", "dialogue": "Texte parlé..."},
    ...
  ]
}
```

Réponds en français. Sois créatif mais concis."""


def chat_scenario(
    chat_history: List[dict],
    user_message: str,
    project_theme: str = "",
    characters: List[dict] = None,
    uploaded_files_context: str = "",
) -> dict:
    """Chat avec Gemini pour créer/affiner un scénario."""
    client = _get_client()

    messages = [{"role": "user", "parts": [{"text": SCENARIO_SYSTEM_PROMPT}]}]

    if project_theme:
        messages.append({
            "role": "user",
            "parts": [{"text": f"Thème du projet : {project_theme}"}],
        })

    if characters:
        chars_desc = "\n".join(
            f"- {c.get('name', '?')}: {c.get('description', 'pas de description')}"
            for c in characters
        )
        messages.append({
            "role": "user",
            "parts": [{"text": f"Personnages du projet :\n{chars_desc}"}],
        })

    if uploaded_files_context:
        messages.append({
            "role": "user",
            "parts": [{"text": f"Contexte des fichiers uploadés :\n{uploaded_files_context}"}],
        })

    messages.append({
        "role": "model",
        "parts": [{"text": "Je suis prêt à créer ton scénario ! Qu'est-ce que tu veux raconter ?"}],
    })

    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "parts": [{"text": msg["content"]}],
        })

    messages.append({"role": "user", "parts": [{"text": user_message}]})

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=messages,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2000,
        ),
    )

    ai_text = response.text

    # Chercher un script JSON dans la réponse
    script_preview = _extract_script_json(ai_text)
    ready = script_preview is not None

    return {
        "ai_message": ai_text,
        "ready_to_validate": ready,
        "script_preview": script_preview,
    }


def _extract_script_json(text: str) -> Optional[dict]:
    """Extrait le script JSON de la réponse IA si présent."""
    # Chercher un bloc ```json ... ```
    import re
    pattern = r"```json\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Chercher { "blocks": [...] } directement
    pattern2 = r'\{\s*"blocks"\s*:\s*\[.*?\]\s*\}'
    match2 = re.search(pattern2, text, re.DOTALL)
    if match2:
        try:
            return json.loads(match2.group(0))
        except json.JSONDecodeError:
            pass

    return None
