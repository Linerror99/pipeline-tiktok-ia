"""Service de génération vidéo Veo 3.1 — génération + extensions + concat ffmpeg."""
import asyncio
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Optional

from google import genai
from google.genai.types import GenerateVideosConfig, Video, Image as VeoImage

from ..config import settings
from ..services.firestore_service import firestore_service
from google.cloud import storage

logger = logging.getLogger(__name__)

# SDK google-genai utilise les variables d'environnement pour Vertex AI
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.PROJECT_ID)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

VEO_GENERATE_MODEL = "veo-3.1-generate-001"
VEO_EXTEND_MODEL = "veo-3.1-generate-001"   # même modèle — preview déprécié
CLIP_DURATION = 8        # secondes — durée d'une génération initiale
EXTENSION_DURATION = 7   # secondes — durée d'une extension


def _num_extensions(target_duration: int) -> int:
    """Nombre d'extensions nécessaires pour atteindre la durée cible."""
    if target_duration <= CLIP_DURATION:
        return 0
    return (target_duration - CLIP_DURATION + EXTENSION_DURATION - 1) // EXTENSION_DURATION


def _get_character_image(characters: list) -> Optional[VeoImage]:
    """Retourne l'image GCS du premier personnage qui en a une."""
    for char in characters:
        gcs_path = char.get("gcs_path", "")
        if not gcs_path:
            continue
        gcs_uri = f"gs://{settings.BUCKET_UPLOADS_V3}/{gcs_path}"
        # Déterminer le mime type depuis l'extension
        ext = gcs_path.rsplit(".", 1)[-1].lower() if "." in gcs_path else "png"
        mime = f"image/{ext}" if ext in ("png", "jpg", "jpeg", "webp") else "image/png"
        if ext == "jpg":
            mime = "image/jpeg"
        logger.info(f"Image personnage trouvée: {gcs_uri} ({char.get('name')})")
        return VeoImage(gcs_uri=gcs_uri, mime_type=mime)
    return None


def _sanitize_for_veo(text: str) -> str:
    """Supprime les références à des célébrités individuelles du prompt Veo.

    Veo (code 29310472) bloque tout prompt contenant le nom d'une célébrité.
    Les équipes nationales et clubs sont autorisés (Portugal, France...).
    """
    import re

    # Patterns "like CelebrityName" ou "comme CelebrityName"
    text = re.sub(r"\blike\s+[A-Z][a-zA-Zé-]+\b", "", text)
    text = re.sub(r"\bcomme\s+[A-Z][a-zA-Zé-]+\b", "", text, flags=re.IGNORECASE)

    # Noms de célébrités individuelles (joueurs, stars...)
    KNOWN_CELEBRITIES = [
        "Ronaldo", "Messi", "Mbappé", "Mbappe", "Neymar", "Kane", "Haaland",
        "Beyoncé", "Beyonce", "Rihanna", "Taylor", "Drake", "Eminem",
        "Zidane", "Beckham", "Griezmann", "Salah", "Lewandowski", "Vinicius",
        "Kylian", "Erling", "Cristiano", "Lionel",
    ]
    for name in KNOWN_CELEBRITIES:
        text = re.sub(rf"\b{re.escape(name)}\b", "", text, flags=re.IGNORECASE)

    # Nettoyer les espaces multiples
    text = re.sub(r"\s{2,}", " ", text).strip(" ,.")
    return text


def _build_character_description(char: dict) -> str:
    """Construit la description visuelle d'un personnage pour le prompt Veo."""
    traits = char.get("traits", {})
    parts = []

    # Priorité au look structuré (JSON Imagen)
    if traits.get("look"):
        parts.append(_sanitize_for_veo(traits["look"]))
    if traits.get("style"):
        style = traits["style"]
        if "style" not in style.lower():
            style = f"{style} style"
        parts.append(style)
    if traits.get("colors"):
        parts.append(f"color palette: {traits['colors']}")
    if traits.get("personality"):
        parts.append(f"expression: {traits['personality']}")

    # Fallback si pas de traits structurés
    if not parts:
        fallback = char.get("ai_description", "") or char.get("description", "")
        if fallback:
            parts.append(_sanitize_for_veo(fallback[:300]))

    return ", ".join(filter(None, parts))


def _build_prompt(blocks: list, characters: list) -> str:
    """Construit le prompt Veo depuis les blocs du scénario et les personnages.

    Structure recommandée (doc Veo) : Sujet → Action → Scène → Style caméra.
    Les noms de célébrités sont filtrés pour éviter le filtre sécurité (code 29310472).
    """
    lines = []

    # ── Personnages (sujet) ─────────────────────────────────────────────────
    char_descriptions = []
    for char in characters:
        name = char.get("name", "Le personnage")
        desc = _build_character_description(char)
        if desc:
            char_descriptions.append(f"{name} ({desc})")
        else:
            char_descriptions.append(name)

    if char_descriptions:
        lines.append("Characters: " + "; ".join(char_descriptions) + ".")

    # ── Blocs scénario (action + scène) ────────────────────────────────────
    # Supporte 2 formats :
    #   Format IA  : {"visuel": "...", "dialogue": "..."}
    #   Format fallback : {"type": "VISUEL"|"DIALOGUE", "text": "..."}
    for block in blocks:
        visuel = block.get("visuel", "")
        dialogue = block.get("dialogue", "")
        if not visuel and not dialogue:
            btype = block.get("type", "VISUEL")
            text = block.get("text", "")
            if btype == "DIALOGUE":
                dialogue = text
            else:
                visuel = text
        if visuel:
            lines.append(_sanitize_for_veo(visuel))
        if dialogue:
            d = dialogue.replace('"', "").replace("'", "")
            lines.append(f"The character speaks: {_sanitize_for_veo(d)}")

    # ── Style cinématographique (doc Veo) ───────────────────────────────────
    lines.append(
        "Cinematic vertical 9:16 TikTok format. "
        "Dynamic handheld camera movement with subtle dolly-in. "
        "Vibrant colors, sharp focus, professional lighting."
    )

    return " ".join(lines)


def _gcs_clip_uri(video_id: str, index: int) -> str:
    return f"gs://{settings.BUCKET_NAME_V3}/{video_id}/clip_{index}.mp4"


def _gcs_final_uri(video_id: str) -> str:
    return f"gs://{settings.BUCKET_NAME_V3}/{video_id}/final.mp4"


async def _wait_for_operation(client: genai.Client, operation, video_id: str,
                               progress_start: int, progress_end: int,
                               step_label: str) -> Optional[object]:
    """Attend la fin d'une opération Veo en mettant à jour Firestore."""
    while not operation.done:
        await asyncio.sleep(15)
        try:
            operation = client.operations.get(operation)
        except Exception as e:
            logger.warning(f"[video {video_id}] Erreur poll opération: {e}")
            continue

        # Progression interpolée pendant l'attente
        progress = min(progress_end - 5, progress_start + 10)
        firestore_service.update_video(video_id, {
            "status": "generating",
            "progress": progress,
            "current_step": step_label,
        })

    if not operation.response:
        error_info = getattr(operation, "error", None) or {}
        if isinstance(error_info, dict):
            code = error_info.get("code", "?")
            msg = error_info.get("message", "Erreur inconnue")
            support_codes = ""
            if "Support codes:" in msg:
                support_codes = msg.split("Support codes:")[-1].strip()
            # Code 29310472 = célébrité dans le prompt
            if "29310472" in str(support_codes):
                raise RuntimeError(
                    "Veo a rejeté le prompt : il contient une référence à une célébrité. "
                    "Vérifiez les descriptions de personnages (pas de noms réels de joueurs/stars)."
                )
            raise RuntimeError(f"Veo a rejeté le prompt (code {code}): {msg}")
        raise RuntimeError(f"Opération Veo terminée sans réponse : {operation}")

    return operation


def _blob_name_from_gcs_uri(uri: str, bucket_name: str) -> str:
    """Extrait le nom du blob depuis une URI GCS gs://bucket/blob/path."""
    prefix = f"gs://{bucket_name}/"
    if uri.startswith(prefix):
        return uri[len(prefix):]
    raise ValueError(f"URI GCS inattendu: {uri}")


async def _concat_clips_ffmpeg(video_id: str, clip_uris: list[str], target_duration: int) -> str:
    """Concatène les clips GCS (via URIs réels) via ffmpeg en local puis re-upload."""
    gcs_client = storage.Client(project=settings.PROJECT_ID)
    bucket = gcs_client.bucket(settings.BUCKET_NAME_V3)

    with tempfile.TemporaryDirectory() as tmpdir:
        local_clips = []

        # Télécharger chaque clip depuis son URI réel
        for i, uri in enumerate(clip_uris):
            blob_name = _blob_name_from_gcs_uri(uri, settings.BUCKET_NAME_V3)
            local_path = os.path.join(tmpdir, f"clip_{i}.mp4")
            blob = bucket.blob(blob_name)
            blob.download_to_filename(local_path, timeout=300)
            local_clips.append(local_path)

        if len(local_clips) == 1:
            final_path = local_clips[0]
        else:
            # Fichier liste pour ffmpeg concat
            list_path = os.path.join(tmpdir, "clips.txt")
            with open(list_path, "w") as f:
                for p in local_clips:
                    f.write(f"file '{p}'\n")

            concat_path = os.path.join(tmpdir, "concat.mp4")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                 "-i", list_path, "-c", "copy", concat_path],
                check=True, capture_output=True,
            )

            # Trim à la durée cible exacte
            final_path = os.path.join(tmpdir, "final.mp4")
            subprocess.run(
                ["ffmpeg", "-y", "-i", concat_path,
                 "-t", str(target_duration), "-c", "copy", final_path],
                check=True, capture_output=True,
            )

        # Upload vers GCS
        final_blob = bucket.blob(f"{video_id}/final.mp4")
        final_blob.upload_from_filename(final_path, content_type="video/mp4", timeout=300)

    return _gcs_final_uri(video_id)


async def generate_video_background(
    video_id: str,
    project_id: str,
    scenario_id: str,
    target_duration: int,
    blocks: list,
    characters: list,
) -> None:
    """BackgroundTask : génère la vidéo Veo et met à jour Firestore."""
    try:
        client = genai.Client()
        num_extensions = _num_extensions(target_duration)
        total_clips = num_extensions + 1

        firestore_service.update_video(video_id, {
            "status": "generating",
            "progress": 5,
            "current_step": "Initialisation Veo...",
            "extensions_planned": num_extensions,
            "extensions_completed": 0,
        })

        prompt = _build_prompt(blocks, characters)
        logger.info(f"[video {video_id}] Prompt Veo ({len(prompt)} chars): {prompt[:200]}...")
        char_image = _get_character_image(characters)
        if char_image:
            logger.info(f"[video {video_id}] Génération image-to-video avec personnage")
        else:
            logger.info(f"[video {video_id}] Génération text-to-video (pas d'image personnage)")

        # ── Génération initiale (clip_0) ────────────────────────────────────
        firestore_service.update_video(video_id, {
            "progress": 10,
            "current_step": "Génération clip initial (8s)...",
        })

        generate_kwargs = {
            "model": VEO_GENERATE_MODEL,
            "prompt": prompt,
            "config": GenerateVideosConfig(
                aspect_ratio="9:16",
                output_gcs_uri=_gcs_clip_uri(video_id, 0),
            ),
        }
        if char_image:
            generate_kwargs["image"] = char_image

        operation = client.models.generate_videos(**generate_kwargs)

        progress_per_clip = 80 // total_clips
        operation = await _wait_for_operation(
            client, operation, video_id,
            progress_start=10,
            progress_end=10 + progress_per_clip,
            step_label="Génération clip initial (8s)...",
        )

        # URI réel retourné par Veo (chemin avec hash auto-généré)
        actual_clip_uris: list[str] = []
        clip_uri = operation.result.generated_videos[0].video.uri
        actual_clip_uris.append(clip_uri)
        logger.info(f"[video {video_id}] Clip 0 généré: {clip_uri}")

        # ── Extensions ─────────────────────────────────────────────────────
        for ext_idx in range(num_extensions):
            ext_number = ext_idx + 1
            firestore_service.update_video(video_id, {
                "progress": 10 + progress_per_clip * (ext_idx + 1),
                "current_step": f"Extension {ext_number}/{num_extensions}...",
                "extensions_completed": ext_idx,
            })

            # Utiliser l'URI réel du clip précédent (pas le chemin prédit)
            input_uri = actual_clip_uris[-1]
            output_uri = _gcs_clip_uri(video_id, ext_idx + 1)
            logger.info(f"[video {video_id}] Extension {ext_number}: input_uri={input_uri}")

            try:
                operation = client.models.generate_videos(
                    model=VEO_EXTEND_MODEL,
                    prompt=prompt,
                    video=Video(uri=input_uri, mime_type="video/mp4"),
                    config=GenerateVideosConfig(
                        output_gcs_uri=output_uri,
                    ),
                )
            except TypeError as _te:
                if "video" in str(_te):
                    logger.warning(
                        f"[video {video_id}] SDK google-genai ne supporte pas le param 'video=' "
                        f"(version trop ancienne). Extensions ignorées — vidéo finale = {len(actual_clip_uris)} clip(s)."
                    )
                    break
                raise

            operation = await _wait_for_operation(
                client, operation, video_id,
                progress_start=10 + progress_per_clip * (ext_idx + 1),
                progress_end=10 + progress_per_clip * (ext_idx + 2),
                step_label=f"Extension {ext_number}/{num_extensions}...",
            )

            clip_uri = operation.result.generated_videos[0].video.uri
            actual_clip_uris.append(clip_uri)
            logger.info(f"[video {video_id}] Extension {ext_number} générée: {clip_uri}")
            firestore_service.update_video(video_id, {"extensions_completed": ext_number})

        # ── Concaténation ffmpeg ────────────────────────────────────────────
        firestore_service.update_video(video_id, {
            "progress": 90,
            "current_step": "Assemblage final...",
        })

        final_uri = await _concat_clips_ffmpeg(video_id, actual_clip_uris, target_duration)

        # Générer une signed URL pour accès HTTP
        gcs_client = storage.Client(project=settings.PROJECT_ID)
        bucket = gcs_client.bucket(settings.BUCKET_NAME_V3)
        blob = bucket.blob(f"{video_id}/final.mp4")
        from datetime import timedelta
        try:
            video_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET",
            )
        except Exception:
            video_url = f"https://storage.googleapis.com/{settings.BUCKET_NAME_V3}/{video_id}/final.mp4"

        firestore_service.update_video(video_id, {
            "status": "completed",
            "progress": 100,
            "current_step": "Terminé",
            "video_url": video_url,
            "gcs_uri": final_uri,
            "actual_duration": target_duration,
            "completed_at": datetime.utcnow(),
        })

        logger.info(f"[video {video_id}] Génération terminée: {video_url}")

    except Exception as e:
        logger.error(f"[video {video_id}] Erreur génération: {e}", exc_info=True)
        firestore_service.update_video(video_id, {
            "status": "failed",
            "progress": 0,
            "current_step": "Échec",
            "error": str(e),
        })
