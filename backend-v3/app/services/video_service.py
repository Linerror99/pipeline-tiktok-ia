"""Service de génération vidéo Veo 3.1 — génération + extensions + concat ffmpeg."""
import asyncio
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Optional

from google import genai
from google.genai.types import GenerateVideosConfig, Image as VeoImage

from ..config import settings
from ..services.firestore_service import firestore_service
from google.cloud import storage

logger = logging.getLogger(__name__)

# SDK google-genai utilise les variables d'environnement pour Vertex AI
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.PROJECT_ID)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

VEO_GENERATE_MODEL = "veo-3.1-generate-001"
CLIP_DURATION = 8        # secondes — durée de chaque clip Veo


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


def _build_prompt_for_block(block: dict, characters: list) -> str:
    """Prompt Veo pour un seul bloc — un clip indépendant de 8s.

    Structure (doc Veo) : Personnage → Action/Scène → Style caméra.
    Chaque clip reçoit la description complète du personnage pour garantir
    la cohérence visuelle à travers toute la vidéo.
    """
    lines = []

    # ── Personnages (sujet) — dans chaque clip pour la cohérence ───────────
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

    # ── Contenu du bloc (visuel + dialogue) ────────────────────────────────
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

    # ── Style cinématographique ─────────────────────────────────────────────
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


# ── Whisper subtitles ───────────────────────────────────────────────────────

_WHISPER_MODEL = None


def _get_whisper_model():
    """Charge le modèle Whisper base une seule fois (mis en cache en mémoire)."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        import whisper as _whisper
        logger.info("Chargement modèle Whisper base...")
        _WHISPER_MODEL = _whisper.load_model("base")
        logger.info("Modèle Whisper chargé.")
    return _WHISPER_MODEL


def _format_ass_time(seconds: float) -> str:
    """Convertit des secondes en format ASS (H:MM:SS.cs)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _generate_subtitles_ass(video_path: str, ass_path: str) -> bool:
    """Transcrit la vidéo avec Whisper et génère un fichier ASS style TikTok.

    Style : 2 mots par ligne, blanc → jaune (highlight), centré en bas.
    Retourne True si des sous-titres ont été générés, False sinon.
    """
    try:
        model = _get_whisper_model()
        result = model.transcribe(video_path, language="fr", word_timestamps=True, verbose=False)

        all_words = []
        for segment in result.get("segments", []):
            for wd in segment.get("words", []):
                word = wd.get("word", "").strip()
                if word:
                    all_words.append({
                        "word": word,
                        "start": wd["start"],
                        "end": wd["end"],
                    })

        if not all_words:
            logger.warning("Whisper: aucun mot détecté dans la vidéo — pas de sous-titres")
            return False

        logger.info(f"Whisper: {len(all_words)} mots transcrits")

        ass_header = """\
[Script Info]
Title: Reetik Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,10,10,80,1
Style: Highlight,Arial Black,95,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,7,3,2,10,10,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for i in range(0, len(all_words), 2):
            group = all_words[i:i + 2]
            t_start = max(0.0, group[0]["start"] - 0.05)
            t_end = max(t_start + 0.1, group[-1]["end"] - 0.05)
            text = " ".join(w["word"].upper() for w in group)
            # Transition blanc → jaune au 35% du temps d'affichage
            t_highlight = t_start + (t_end - t_start) * 0.35
            events.append(
                f"Dialogue: 0,{_format_ass_time(t_start)},{_format_ass_time(t_highlight)},Default,,0,0,0,,{text}"
            )
            events.append(
                f"Dialogue: 0,{_format_ass_time(t_highlight)},{_format_ass_time(t_end)},Highlight,,0,0,0,,{text}"
            )

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_header)
            f.write("\n".join(events))

        logger.info(f"Fichier ASS généré: {len(events)} événements")
        return True

    except Exception as e:
        logger.warning(f"Whisper subtitle generation failed: {e}", exc_info=True)
        return False


def _burn_subtitles(input_path: str, ass_path: str, output_path: str) -> bool:
    """Brûle un fichier ASS dans la vidéo via ffmpeg (re-encode vidéo, copie audio)."""
    try:
        # Échapper le chemin pour le filtre ffmpeg (backslashes et ':' problématiques)
        safe_ass = ass_path.replace("\\", "/").replace(":", "\\:")
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", input_path,
                "-vf", f"ass={safe_ass}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "copy",
                output_path,
            ],
            check=True, capture_output=True,
        )
        logger.info("Sous-titres gravés dans la vidéo.")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"ffmpeg subtitle burn failed: {e.stderr.decode()[-500:]}")
        return False


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

        # ── Sous-titres Whisper ─────────────────────────────────────────────
        ass_path = os.path.join(tmpdir, "subtitles.ass")
        subtitled_path = os.path.join(tmpdir, "final_subtitled.mp4")
        if _generate_subtitles_ass(final_path, ass_path):
            if _burn_subtitles(final_path, ass_path, subtitled_path):
                final_path = subtitled_path
            else:
                logger.warning(f"[video {video_id}] Burn-in sous-titres échoué — vidéo sans sous-titres")
        else:
            logger.warning(f"[video {video_id}] Transcription Whisper vide — vidéo sans sous-titres")

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
    """BackgroundTask : génère la vidéo Veo (1 clip indépendant par bloc) et met à jour Firestore."""
    try:
        client = genai.Client()
        num_clips = len(blocks)   # 1 clip par bloc = chaque scène dans son propre clip 8s
        if num_clips == 0:
            raise ValueError("Le scénario ne contient aucun bloc")

        firestore_service.update_video(video_id, {
            "status": "generating",
            "progress": 5,
            "current_step": f"Initialisation ({num_clips} scènes)...",
            "extensions_planned": 0,
            "extensions_completed": 0,
        })

        char_image = _get_character_image(characters)
        if char_image:
            logger.info(f"[video {video_id}] Mode image-to-video (personnage trouvé)")
        else:
            logger.info(f"[video {video_id}] Mode text-to-video (pas d'image personnage)")

        # ── Génération : 1 clip indépendant par bloc ───────────────────────
        # Chaque clip reçoit son propre prompt (personnage + scène du bloc).
        # Aucune extension vidéo-vers-vidéo → pas de filtre person/face 17301594.
        actual_clip_uris: list[str] = []
        progress_per_clip = 80 // num_clips

        for block_idx, block in enumerate(blocks):
            clip_label = f"Scène {block_idx + 1}/{num_clips}"
            p_start = 10 + progress_per_clip * block_idx
            p_end = 10 + progress_per_clip * (block_idx + 1)

            firestore_service.update_video(video_id, {
                "progress": p_start,
                "current_step": f"Génération {clip_label}...",
            })

            block_prompt = _build_prompt_for_block(block, characters)
            logger.info(f"[video {video_id}] {clip_label} prompt ({len(block_prompt)} chars): {block_prompt[:150]}...")

            generate_kwargs = {
                "model": VEO_GENERATE_MODEL,
                "prompt": block_prompt,
                "config": GenerateVideosConfig(
                    aspect_ratio="9:16",
                    output_gcs_uri=_gcs_clip_uri(video_id, block_idx),
                ),
            }
            # L'image du personnage est passée à chaque clip → cohérence visuelle
            if char_image:
                generate_kwargs["image"] = char_image

            operation = client.models.generate_videos(**generate_kwargs)
            operation = await _wait_for_operation(
                client, operation, video_id,
                progress_start=p_start,
                progress_end=p_end,
                step_label=f"Génération {clip_label}...",
            )

            clip_uri = operation.result.generated_videos[0].video.uri
            actual_clip_uris.append(clip_uri)
            logger.info(f"[video {video_id}] {clip_label} générée: {clip_uri}")

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
