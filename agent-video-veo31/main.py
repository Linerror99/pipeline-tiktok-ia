"""
Agent Video Veo 3.1 — Cloud Function Gen2
Génère une vidéo continue avec extensions séquentielles Veo 3.1.
Résout le problème des coupures audio de V2 (clips parallèles indépendants).

Déclenchée par upload de {video_id}/script_v3.json dans le bucket V3.
Produit UNE vidéo initiale de 8s, puis un Cloud Scheduler poll pour les extensions.

Modèle : veo-3.1-generate-001 (GA)
Durées : 8s / 15s / 22s / 29s / 36s / 43s / 50s / 57s max
Formule : 8 + N×7 (N = 0 à 7 extensions)
"""
import functions_framework
from google.cloud import storage, firestore
from google import genai
from google.genai import types
import os
import json
from datetime import datetime

storage_client = storage.Client()

PROJECT_ID = os.environ.get("GCP_PROJECT", "reetik-project")
FIRESTORE_DATABASE = os.environ.get("FIRESTORE_DATABASE", "reetik-v3")
firestore_client = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME_V3", "reetik-v3-artifacts")

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Durées supportées : 8s initial + N×7s extensions
VALID_DURATIONS = [8, 15, 22, 29, 36, 43, 50, 57]

# Modèle Veo 3.1 GA (deadline preview : 2 avril 2026)
VEO_MODEL = "veo-3.1-generate-001"


def calculate_extensions(target_duration: int) -> int:
    """Calcule le nombre d'extensions nécessaires pour atteindre la durée cible."""
    if target_duration <= 8:
        return 0
    return min((target_duration - 8) // 7, 7)


def snap_to_valid_duration(target_duration: int) -> int:
    """Arrondit à la durée valide la plus proche (supérieure ou égale)."""
    for d in VALID_DURATIONS:
        if target_duration <= d:
            return d
    return 57  # Max Veo 3.1


def build_prompt(block_data: dict, character_refs: list, is_initial: bool = True) -> str:
    """Construit le prompt Veo 3.1 avec références personnages."""
    visual = block_data.get("visuel", "")
    dialogue = block_data.get("dialogue", "")

    prompt = visual
    if dialogue:
        prompt += f'\n\nDialogue à générer en audio: "{dialogue}"'

    if not is_initial:
        prompt = f"Suite de la scène précédente. {prompt}"

    # Ajouter contexte personnages si disponible
    if character_refs:
        chars_desc = ", ".join(
            ref.get("name", "personnage") for ref in character_refs if isinstance(ref, dict)
        )
        if chars_desc:
            prompt += f"\n\nPersonnages présents: {chars_desc}"

    return prompt


@functions_framework.cloud_event
def generate_video_veo31(cloudevent):
    """
    Cloud Function V3 — Génère la vidéo initiale 8s avec Veo 3.1.

    Déclenchée par upload de script_v3.json dans le bucket V3.
    Le monitoring des extensions est géré par monitor-extensions-v3 (Cloud Scheduler).
    """
    try:
        data = cloudevent.data
        file_name = data["name"]

        if not file_name.endswith("/script_v3.json"):
            return "OK"

        video_id = file_name.split("/")[0]
        print(f"🎬 [V3] Génération Veo 3.1 pour video_id: {video_id}")

    except Exception as e:
        print(f"❌ Erreur parsing CloudEvent: {e}")
        return "ERROR"

    try:
        # 1. Charger script V3
        bucket = storage_client.bucket(BUCKET_NAME)
        script_blob = bucket.blob(f"{video_id}/script_v3.json")

        if not script_blob.exists():
            print(f"❌ Script {video_id}/script_v3.json non trouvé dans {BUCKET_NAME}")
            return "ERROR"

        script_data = json.loads(script_blob.download_as_text())
        blocks = script_data.get("blocks", [])
        target_duration = script_data.get("target_duration", 8)
        character_refs = script_data.get("character_references", [])

        if not blocks:
            print(f"❌ Aucun bloc dans le script {video_id}")
            return "ERROR"

        actual_duration = snap_to_valid_duration(target_duration)
        num_extensions = calculate_extensions(actual_duration)

        print(f"📊 Blocs: {len(blocks)}, Durée cible: {actual_duration}s, Extensions: {num_extensions}")

        # Update Firestore status
        firestore_client.collection("videos_v3").document(video_id).update({
            "status": "generating",
            "target_duration": actual_duration,
            "extensions_planned": num_extensions,
            "updated_at": firestore.SERVER_TIMESTAMP,
        })

        # 2. Générer vidéo initiale (8s)
        block_1 = blocks[0]
        initial_prompt = build_prompt(block_1, character_refs, is_initial=True)

        print(f"🎥 Vidéo initiale 8s — Prompt: {initial_prompt[:120]}...")

        try:
            initial_operation = genai_client.models.generate_videos(
                model=VEO_MODEL,
                prompt=initial_prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    resolution="720p",
                    duration_seconds=8,
                    person_generation="allow_all",
                ),
            )
        except Exception as gen_err:
            error_msg = str(gen_err)
            print(f"❌ Erreur génération initiale: {error_msg}")

            # Fallback si erreur de safety/guidelines
            if "usage guidelines" in error_msg.lower() or "third-party" in error_msg.lower():
                print("🔄 Tentative avec prompt de secours...")
                fallback_prompt = (
                    "Scène abstraite colorée avec des formes géométriques en mouvement. "
                    "Style moderne et épuré. Animation fluide et dynamique."
                )
                initial_operation = genai_client.models.generate_videos(
                    model=VEO_MODEL,
                    prompt=fallback_prompt,
                    config=types.GenerateVideosConfig(
                        aspect_ratio="9:16",
                        resolution="720p",
                        duration_seconds=8,
                        person_generation="allow_all",
                    ),
                )
            else:
                raise

        print(f"✅ Opération initiale lancée: {initial_operation.name[:80]}...")

        # 3. Stocker opération dans Firestore pour monitoring par Cloud Scheduler
        firestore_client.collection("v3_veo_operations").document(video_id).set({
            "video_id": video_id,
            "status": "generating_initial",
            "initial_operation": initial_operation.name,
            "current_operation": initial_operation.name,
            "extensions_operations": [],
            "total_extensions": num_extensions,
            "completed_extensions": 0,
            "current_video_gcs_uri": None,
            "blocks": blocks,
            "character_references": character_refs,
            "target_duration": actual_duration,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "retry_count": 0,
        })

        print(
            f"✅ Génération V3 lancée — {actual_duration}s "
            f"({num_extensions} extension(s) à suivre via Cloud Scheduler)"
        )
        return "OK"

    except Exception as e:
        print(f"❌ Erreur génération V3: {e}")
        import traceback
        traceback.print_exc()

        try:
            firestore_client.collection("videos_v3").document(video_id).update({
                "status": "failed",
                "error": str(e)[:500],
                "updated_at": firestore.SERVER_TIMESTAMP,
            })
        except Exception:
            pass

        return "ERROR"
