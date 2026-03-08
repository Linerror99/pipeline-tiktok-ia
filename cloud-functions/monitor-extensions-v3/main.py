"""
Monitor Extensions V3 — Cloud Function Gen2 (HTTP trigger)
Vérifie les opérations Veo 3.1 en cours et lance les extensions séquentiellement.

Appelée par Cloud Scheduler toutes les 30-60 secondes.
Flow :
  1. Query Firestore pour les opérations V3 en attente
  2. Pour chaque opération :
     - Vérifier statut via REST API Vertex AI
     - Si vidéo initiale terminée → lancer extension 1 (ou finaliser si 0 extensions)
     - Si extension N terminée → lancer extension N+1 (ou finaliser si dernière)
  3. Quand toutes extensions terminées → copier vidéo finale dans bucket V3
"""
import functions_framework
from google.cloud import storage, firestore
import google.auth
from google.auth.transport.requests import Request
import requests as http_requests
import os
import json
from datetime import datetime

storage_client = storage.Client()
credentials, project_id = google.auth.default()

PROJECT_ID = os.environ.get("GCP_PROJECT", project_id or "reetik-project")
FIRESTORE_DATABASE = os.environ.get("FIRESTORE_DATABASE", "reetik-v3")
firestore_client = firestore.Client(project=PROJECT_ID, database=FIRESTORE_DATABASE)
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME_V3", "reetik-v3-artifacts")
VEO_MODEL = "veo-3.1-generate-001"


def get_access_token():
    """Récupère un token d'accès OAuth2 pour l'API Vertex AI."""
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token


def check_operation_status(operation_name: str) -> dict:
    """
    Vérifie le statut d'une opération Veo via REST API.
    Returns: {"status": "pending"|"success"|"failed", "video_gcs_uri": str|None, "error": str|None}
    """
    try:
        parts = operation_name.split("/")
        if len(parts) < 6:
            return {"status": "failed", "video_gcs_uri": None, "error": "Invalid operation name"}

        location = parts[3]
        api_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/{operation_name}"
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json",
        }

        response = http_requests.get(api_endpoint, headers=headers, timeout=30)

        if response.status_code == 200:
            op_data = response.json()

            if op_data.get("done", False):
                if "error" in op_data:
                    error_msg = op_data["error"].get("message", "Unknown error")
                    return {"status": "failed", "video_gcs_uri": None, "error": error_msg}

                # Extraire l'URI GCS de la vidéo générée
                result = op_data.get("response", {})
                generated_samples = result.get("generatedSamples", [])
                if generated_samples:
                    gcs_uri = generated_samples[0].get("gcsUri")
                    return {"status": "success", "video_gcs_uri": gcs_uri, "error": None}
                else:
                    return {"status": "failed", "video_gcs_uri": None, "error": "No generated samples"}
            else:
                return {"status": "pending", "video_gcs_uri": None, "error": None}

        elif response.status_code == 404:
            # Opération expirée — vérifier GCS directement
            print(f"⚠️ Opération expirée (404): {operation_name[:60]}")
            return {"status": "failed", "video_gcs_uri": None, "error": "Operation expired (404)"}
        else:
            return {"status": "failed", "video_gcs_uri": None, "error": f"API error: {response.status_code}"}

    except Exception as e:
        return {"status": "failed", "video_gcs_uri": None, "error": str(e)}


def launch_extension_rest(video_gcs_uri: str, prompt: str) -> str:
    """
    Lance une extension Veo 3.1 (7s supplémentaires) via REST API.
    Passe la vidéo existante comme référence pour la continuation.
    Returns: operation_name
    """
    api_endpoint = (
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/"
        f"projects/{PROJECT_ID}/locations/{LOCATION}/"
        f"publishers/google/models/{VEO_MODEL}:predictLongRunning"
    )

    # Corps de requête pour extension vidéo
    # Le champ "video" avec gcsUri indique à Veo de continuer cette vidéo
    body = {
        "instances": [
            {
                "prompt": prompt,
                "video": {
                    "gcsUri": video_gcs_uri,
                    "mimeType": "video/mp4",
                },
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16",
            "personGeneration": "allow_all",
        },
    }

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = http_requests.post(api_endpoint, json=body, headers=headers, timeout=60)

    if response.status_code != 200:
        raise Exception(
            f"Extension API error {response.status_code}: {response.text[:300]}"
        )

    op_data = response.json()
    operation_name = op_data.get("name", "")

    if not operation_name:
        raise Exception(f"No operation name in response: {json.dumps(op_data)[:300]}")

    return operation_name


def build_extension_prompt(blocks: list, ext_number: int, character_refs: list) -> str:
    """Construit le prompt pour l'extension N."""
    # Utiliser le bloc correspondant (ou le dernier si pas assez de blocs)
    block_index = min(ext_number, len(blocks) - 1)
    block = blocks[block_index]

    visual = block.get("visuel", "")
    dialogue = block.get("dialogue", "")

    prompt = f"Suite de la scène précédente. {visual}"
    if dialogue:
        prompt += f'\n\nDialogue à générer en audio: "{dialogue}"'

    if character_refs:
        chars_desc = ", ".join(
            ref.get("name", "personnage") for ref in character_refs if isinstance(ref, dict)
        )
        if chars_desc:
            prompt += f"\n\nPersonnages présents: {chars_desc}"

    return prompt


def copy_video_to_v3_bucket(source_gcs_uri: str, video_id: str) -> str:
    """
    Copie la vidéo finale depuis le bucket Veo vers le bucket V3.
    Returns: destination GCS URI
    """
    # Parse source URI: gs://bucket/path/to/file.mp4
    if not source_gcs_uri.startswith("gs://"):
        raise Exception(f"Invalid GCS URI: {source_gcs_uri}")

    parts = source_gcs_uri[5:].split("/", 1)
    source_bucket_name = parts[0]
    source_blob_name = parts[1] if len(parts) > 1 else ""

    source_bucket = storage_client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)

    dest_bucket = storage_client.bucket(BUCKET_NAME)
    dest_blob_name = f"{video_id}/final.mp4"

    source_bucket.copy_blob(source_blob, dest_bucket, dest_blob_name)

    dest_uri = f"gs://{BUCKET_NAME}/{dest_blob_name}"
    print(f"✅ Vidéo copiée: {source_gcs_uri} → {dest_uri}")
    return dest_uri


def finalize_video(video_id: str, video_gcs_uri: str, data: dict):
    """Finalise la vidéo : copie dans bucket V3 et met à jour Firestore."""
    try:
        final_uri = copy_video_to_v3_bucket(video_gcs_uri, video_id)
    except Exception as e:
        print(f"⚠️ Erreur copie vidéo, utilisation URI source: {e}")
        final_uri = video_gcs_uri

    target_duration = data.get("target_duration", 8)

    # Update videos_v3
    firestore_client.collection("videos_v3").document(video_id).update({
        "status": "completed",
        "video_url": final_uri,
        "has_native_audio": True,
        "actual_duration": target_duration,
        "generation_completed_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })

    # Update v3_veo_operations
    firestore_client.collection("v3_veo_operations").document(video_id).update({
        "status": "completed",
        "current_video_gcs_uri": final_uri,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })

    print(f"🏁 Vidéo {video_id} finalisée — {target_duration}s — {final_uri}")


def mark_failed(video_id: str, error: str):
    """Marque une vidéo comme échouée."""
    print(f"❌ Vidéo {video_id} échouée: {error}")

    firestore_client.collection("videos_v3").document(video_id).update({
        "status": "failed",
        "error": error[:500],
        "updated_at": firestore.SERVER_TIMESTAMP,
    })
    firestore_client.collection("v3_veo_operations").document(video_id).update({
        "status": "failed",
        "error": error[:500],
        "updated_at": firestore.SERVER_TIMESTAMP,
    })


def process_operation(video_id: str, data: dict):
    """Traite une opération V3 en cours."""
    status = data["status"]
    total_ext = data["total_extensions"]
    completed_ext = data["completed_extensions"]
    current_op = data.get("current_operation", "")
    retry_count = data.get("retry_count", 0)

    if not current_op:
        mark_failed(video_id, "No current operation")
        return

    # Vérifier statut de l'opération en cours
    op_result = check_operation_status(current_op)
    op_status = op_result["status"]

    if op_status == "pending":
        # Toujours en cours, rien à faire
        return

    if op_status == "failed":
        error = op_result.get("error", "Unknown")

        # Retry (max 2 tentatives)
        if retry_count < 2:
            print(f"🔄 Retry {retry_count + 1}/2 pour {video_id}: {error}")
            firestore_client.collection("v3_veo_operations").document(video_id).update({
                "retry_count": retry_count + 1,
                "updated_at": firestore.SERVER_TIMESTAMP,
            })
            # La prochaine itération du scheduler re-vérifiera
            # TODO: relancer la génération/extension échouée
        else:
            mark_failed(video_id, f"Max retries reached. Last error: {error}")
        return

    # Opération réussie
    video_gcs_uri = op_result["video_gcs_uri"]
    if not video_gcs_uri:
        mark_failed(video_id, "Operation succeeded but no GCS URI returned")
        return

    if status == "generating_initial":
        # Vidéo initiale terminée
        print(f"✅ Vidéo initiale terminée pour {video_id}: {video_gcs_uri[:80]}")

        if total_ext == 0:
            # Pas d'extensions, vidéo finale directement
            finalize_video(video_id, video_gcs_uri, data)
        else:
            # Lancer extension 1
            blocks = data.get("blocks", [])
            character_refs = data.get("character_references", [])
            prompt = build_extension_prompt(blocks, 1, character_refs)

            print(f"🔄 Extension 1/{total_ext} pour {video_id}")
            try:
                ext_op_name = launch_extension_rest(video_gcs_uri, prompt)
                firestore_client.collection("v3_veo_operations").document(video_id).update({
                    "status": "extending_1",
                    "current_operation": ext_op_name,
                    "current_video_gcs_uri": video_gcs_uri,
                    "completed_extensions": 0,
                    "extensions_operations": firestore.ArrayUnion([ext_op_name]),
                    "retry_count": 0,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                })
            except Exception as e:
                mark_failed(video_id, f"Extension 1 launch failed: {e}")

    elif status.startswith("extending_"):
        # Extension terminée
        new_completed = completed_ext + 1
        print(f"✅ Extension {new_completed}/{total_ext} terminée pour {video_id}")

        if new_completed >= total_ext:
            # Toutes les extensions terminées → vidéo finale
            finalize_video(video_id, video_gcs_uri, data)
        else:
            # Lancer extension suivante
            next_ext = new_completed + 1
            blocks = data.get("blocks", [])
            character_refs = data.get("character_references", [])
            prompt = build_extension_prompt(blocks, next_ext, character_refs)

            print(f"🔄 Extension {next_ext}/{total_ext} pour {video_id}")
            try:
                ext_op_name = launch_extension_rest(video_gcs_uri, prompt)
                firestore_client.collection("v3_veo_operations").document(video_id).update({
                    "status": f"extending_{next_ext}",
                    "current_operation": ext_op_name,
                    "current_video_gcs_uri": video_gcs_uri,
                    "completed_extensions": new_completed,
                    "extensions_operations": firestore.ArrayUnion([ext_op_name]),
                    "retry_count": 0,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                })
            except Exception as e:
                mark_failed(video_id, f"Extension {next_ext} launch failed: {e}")


@functions_framework.http
def check_all_pending(request):
    """
    Cloud Function HTTP — Vérifie toutes les opérations V3 en attente.
    Appelée par Cloud Scheduler toutes les 30-60 secondes.
    """
    try:
        # Query toutes les opérations non terminées
        ops_ref = firestore_client.collection("v3_veo_operations")
        pending_ops = []

        # Firestore ne supporte pas != directement sur plusieurs valeurs
        # On query tout et on filtre côté client (volume faible)
        all_ops = ops_ref.stream()

        for doc in all_ops:
            data = doc.to_dict()
            status = data.get("status", "")
            if status not in ("completed", "failed"):
                pending_ops.append((doc.id, data))

        if not pending_ops:
            return json.dumps({"message": "No pending operations", "count": 0}), 200

        print(f"📊 {len(pending_ops)} opération(s) V3 en attente")

        results = []
        for video_id, data in pending_ops:
            try:
                process_operation(video_id, data)
                results.append({"video_id": video_id, "processed": True})
            except Exception as e:
                print(f"❌ Erreur traitement {video_id}: {e}")
                results.append({"video_id": video_id, "processed": False, "error": str(e)[:200]})

        return json.dumps({
            "message": f"Processed {len(results)} operations",
            "count": len(results),
            "results": results,
        }), 200

    except Exception as e:
        print(f"❌ Erreur check_all_pending: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({"error": str(e)[:300]}), 500
