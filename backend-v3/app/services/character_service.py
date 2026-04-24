"""Service Personnages V3 — Génération d'images avec Imagen 4."""
from google import genai
from google.genai import types
from google.cloud import storage
import io
import base64
import uuid

from ..config import settings

IMAGEN_MODEL = "imagen-4.0-generate-001"

_client = None
_storage_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=settings.PROJECT_ID,
            location=settings.REGION,
        )
    return _client


def _get_storage_client():
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=settings.PROJECT_ID)
    return _storage_client


def build_character_prompt(traits: dict) -> str:
    """Construit un prompt Imagen 4 à partir des traits structurés du personnage."""
    parts = []

    # 1. Le look en anglais — issu du JSON structuré généré par Gemini (le plus important)
    if traits.get("look"):
        parts.append(traits["look"])
    # Fallback : description brute (ai_description) seulement si pas de look structuré
    # On ne l'utilise pas directement car c'est souvent du texte conversationnel
    # avec emojis et bullets qui pollue le prompt Imagen.

    # 2. Style artistique
    style = traits.get("style", "anime shonen style")
    if "style" not in style.lower():
        style = f"{style} style"
    parts.append(style)

    # 3. Nom du personnage (léger ancrage)
    if traits.get("name"):
        parts.append(f"character named '{traits['name']}'")

    # 4. Couleurs dominantes
    if traits.get("colors"):
        parts.append(f"color palette: {traits['colors']}")

    # 5. Expression / attitude
    if traits.get("personality"):
        parts.append(f"expression: {traits['personality']}")

    # 6. Specs techniques Imagen
    parts.append("full body pose, clean gradient background, portrait vertical format")
    parts.append("high quality detailed illustration, consistent character design, sharp linework")

    return ", ".join(filter(None, parts))


async def generate_character_image(
    character_id: str,
    project_id: str,
    traits: dict,
    custom_prompt: str = None,
) -> dict:
    """Génère une image de personnage avec Imagen 4 et la stocke dans GCS."""
    client = _get_client()

    prompt = custom_prompt if custom_prompt else build_character_prompt(traits)

    response = client.models.generate_images(
        model=IMAGEN_MODEL,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="9:16",
            person_generation="allow_all",
        ),
    )

    if not response.generated_images:
        return {"success": False, "error": "Imagen 4 n'a pas généré d'image. Essayez un prompt différent."}

    image = response.generated_images[0]
    image_bytes = image.image.image_bytes

    # Upload vers GCS
    storage_client = _get_storage_client()
    bucket = storage_client.bucket(settings.BUCKET_UPLOADS_V3)
    image_filename = f"characters/{project_id}/{character_id}/{uuid.uuid4().hex}.png"
    blob = bucket.blob(image_filename)
    blob.upload_from_string(image_bytes, content_type="image/png", timeout=300)

    # URL signée pour accès
    from datetime import timedelta
    signed_url = blob.generate_signed_url(expiration=timedelta(hours=24))

    return {
        "success": True,
        "image_url": f"gs://{settings.BUCKET_UPLOADS_V3}/{image_filename}",
        "signed_url": signed_url,
        "gcs_path": image_filename,
    }


async def generate_character_variations(
    character_id: str,
    project_id: str,
    traits: dict,
    count: int = 3,
) -> list:
    """Génère plusieurs variations du personnage."""
    count = min(count, 4)  # Imagen 4 max 4 images par requête
    client = _get_client()

    prompt = build_character_prompt(traits)

    response = client.models.generate_images(
        model=IMAGEN_MODEL,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=count,
            aspect_ratio="9:16",
            person_generation="allow_all",
        ),
    )

    if not response.generated_images:
        return []

    storage_client = _get_storage_client()
    bucket = storage_client.bucket(settings.BUCKET_UPLOADS_V3)
    results = []

    for i, gen_img in enumerate(response.generated_images):
        image_bytes = gen_img.image.image_bytes
        image_filename = f"characters/{project_id}/{character_id}/var_{uuid.uuid4().hex}.png"
        blob = bucket.blob(image_filename)
        blob.upload_from_string(image_bytes, content_type="image/png", timeout=300)

        from datetime import timedelta
        signed_url = blob.generate_signed_url(expiration=timedelta(hours=24))

        results.append({
            "image_url": f"gs://{settings.BUCKET_UPLOADS_V3}/{image_filename}",
            "signed_url": signed_url,
            "gcs_path": image_filename,
        })

    return results
