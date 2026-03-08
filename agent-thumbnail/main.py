"""Agent Thumbnail V3 — Génération de miniatures TikTok avec Imagen 4.

Cloud Function Gen2 déclenchée quand une vidéo passe au statut "completed".
Génère automatiquement une miniature 9:16 basée sur le scénario et les personnages.
"""
import functions_framework
from google import genai
from google.genai import types
from google.cloud import firestore, storage
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-thumbnail")

PROJECT_ID = "reetik-project"
REGION = "us-central1"
IMAGEN_MODEL = "imagen-4.0-generate-001"
BUCKET_THUMBNAILS = "reetik-v3-thumbnails"
BUCKET_UPLOADS = "reetik-v3-uploads"


def get_genai_client():
    return genai.Client(vertexai=True, project=PROJECT_ID, location=REGION)


FIRESTORE_DATABASE = "reetik-v3"


def get_firestore_client():
    return firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)


def get_storage_client():
    return storage.Client(project=PROJECT_ID)


@functions_framework.http
def generate_thumbnail(request):
    """HTTP endpoint — appelé par monitor-extensions-v3 quand la vidéo est complète.

    Body JSON: {"video_id": "...", "project_id": "..."}
    """
    data = request.get_json(silent=True)
    if not data or "video_id" not in data:
        return {"error": "video_id requis"}, 400

    video_id = data["video_id"]
    project_id = data.get("project_id", "")

    logger.info(f"Génération thumbnail pour video={video_id}")

    db = get_firestore_client()

    # Charger la vidéo
    video_ref = db.collection("videos_v3").document(video_id)
    video_doc = video_ref.get()
    if not video_doc.exists:
        return {"error": "Vidéo non trouvée"}, 404

    video = video_doc.to_dict()
    video["id"] = video_id

    # Charger le scénario
    scenario_id = video.get("scenario_id")
    scenario = {}
    if scenario_id:
        scen_doc = db.collection("scenarios").document(scenario_id).get()
        if scen_doc.exists:
            scenario = scen_doc.to_dict()

    # Charger les personnages
    character_ids = scenario.get("character_ids", [])
    characters = []
    for cid in character_ids:
        char_doc = db.collection("characters").document(cid).get()
        if char_doc.exists:
            characters.append(char_doc.to_dict())

    # Construire le prompt
    prompt = build_thumbnail_prompt(video, scenario, characters)
    logger.info(f"Prompt thumbnail: {prompt[:200]}...")

    # Générer avec Imagen 4
    try:
        client = get_genai_client()
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
            logger.warning("Imagen 4 n'a pas généré d'image, tentative avec prompt simplifié")
            simple_prompt = build_simple_prompt(video, scenario)
            response = client.models.generate_images(
                model=IMAGEN_MODEL,
                prompt=simple_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    person_generation="allow_all",
                ),
            )

        if not response.generated_images:
            logger.error("Impossible de générer la miniature")
            return {"error": "Génération échouée"}, 500

        image_bytes = response.generated_images[0].image.image_bytes

        # Upload vers GCS
        storage_client = get_storage_client()
        bucket = storage_client.bucket(BUCKET_THUMBNAILS)
        blob_name = f"{video_id}/thumbnail_{uuid.uuid4().hex[:8]}.png"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(image_bytes, content_type="image/png")

        thumbnail_gcs = f"gs://{BUCKET_THUMBNAILS}/{blob_name}"
        logger.info(f"Thumbnail uploadée: {thumbnail_gcs}")

        # Mettre à jour Firestore
        video_ref.update({
            "thumbnail_url": thumbnail_gcs,
            "thumbnail_gcs_path": blob_name,
        })

        return {
            "success": True,
            "video_id": video_id,
            "thumbnail_url": thumbnail_gcs,
        }

    except Exception as e:
        logger.error(f"Erreur génération thumbnail: {e}")
        return {"error": str(e)}, 500


def build_thumbnail_prompt(video: dict, scenario: dict, characters: list) -> str:
    """Construit un prompt Imagen 4 pour la miniature TikTok."""
    parts = [
        "Eye-catching TikTok video thumbnail, vertical 9:16 format",
        "Bold and vibrant, designed to maximize clicks",
    ]

    # Premier bloc du scénario comme contexte visuel
    script = scenario.get("script", {})
    blocks = script.get("blocks", [])
    if blocks:
        first_visual = blocks[0].get("visuel", "")
        if first_visual:
            parts.append(f"Scene: {first_visual[:150]}")

    # Personnages
    for char in characters[:2]:  # Max 2 personnages dans la miniature
        name = char.get("name", "")
        traits = char.get("traits", {})
        style = traits.get("style", "")
        if name:
            parts.append(f"featuring character '{name}' in {style} style" if style else f"featuring '{name}'")

    parts.extend([
        "High contrast, bright colors, professional quality",
        "No text overlay, clean composition",
    ])

    return ", ".join(parts)


def build_simple_prompt(video: dict, scenario: dict) -> str:
    """Prompt simplifié en cas d'échec du premier."""
    title = scenario.get("title", "TikTok video")
    return (
        f"Colorful TikTok thumbnail for a video about '{title}', "
        "vertical 9:16, vibrant colors, eye-catching, professional quality, "
        "clean background, high contrast"
    )
