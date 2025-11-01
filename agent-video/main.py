import functions_framework
from google.cloud import storage
import google.auth
from google.auth.transport.requests import Request
import requests
import os

storage_client = storage.Client()
credentials, project_id = google.auth.default()

def get_access_token():
    """Récupère un token d'accès pour l'API Vertex AI"""
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token

@functions_framework.cloud_event
def generate_video(cloudevent):
    data = cloudevent.data
    bucket_name = data["bucket"]
    audio_file_name = data["name"]

    print(f"Déclencheur reçu pour le fichier audio : {audio_file_name}")

    if not audio_file_name.startswith("audio_") or not audio_file_name.endswith(".mp3"):
        print(f"Fichier non-audio {audio_file_name}. Traitement ignoré.")
        return "OK"

    # --- Lecture du script ---
    script_file_name = audio_file_name.replace("audio_", "script_").replace(".mp3", ".txt")
    try:
        bucket = storage_client.bucket(bucket_name)
        script_blob = bucket.blob(script_file_name)
        if not script_blob.exists():
            print(f"Erreur: script {script_file_name} non trouvé.")
            return "Error: Script not found"
        script_content = script_blob.download_as_text(encoding="utf-8")
    except Exception as e:
        print(f"Erreur lors de la lecture du script : {e}")
        return

    # --- Extraction des prompts ---
    visual_prompts = []
    base_style_prompt = "Cinematic, photorealistic, vibrant colors. "
    for line in script_content.splitlines():
        upper_line = line.strip().upper()
        marker_pos = upper_line.find("VISUEL")
        if marker_pos != -1:
            colon_pos = upper_line.find(":", marker_pos)
            if colon_pos != -1:
                text_part = line.strip()[colon_pos + 1:]
                prompt_text = text_part.strip().replace('*', '').replace('#', '')
                full_prompt = base_style_prompt + prompt_text
                visual_prompts.append(full_prompt)

    if not visual_prompts:
        print("Aucun prompt visuel trouvé. Arrêt.")
        return "OK"

    print(f"{len(visual_prompts)} prompts visuels extraits. Lancement des tâches de génération vidéo...")

    # --- Appel API REST selon la documentation officielle ---
    try:
        video_base_name = os.path.splitext(audio_file_name.replace("audio_", ""))[0]
        location = "us-central1"
        model_id = "veo-3.0-generate-001"
        
        # URL de l'API selon la documentation
        api_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        for i, prompt in enumerate(visual_prompts):
            # Dossier de sortie pour ce clip spécifique
            output_storage_uri = f"gs://{bucket_name}/video_clips/{video_base_name}/clip_{i+1}/"
            
            print(f"  - Lancement tâche pour prompt {i+1}. Sortie vers : {output_storage_uri}")

            # Structure du JSON selon la documentation officielle
            request_body = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "storageUri": output_storage_uri,
                    "sampleCount": 1,
                    "aspectRatio": "9:16",
                    "durationSecs": 4
                }
            }

            # Appel à l'API
            response = requests.post(api_endpoint, headers=headers, json=request_body)
            
            if response.status_code == 200:
                operation_data = response.json()
                operation_name = operation_data.get('name', 'N/A')
                print(f"    -> Tâche lancée avec succès. Opération : {operation_name}")
            else:
                print(f"    -> Erreur API (code {response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"Erreur lors du lancement de la génération vidéo : {e}")
        import traceback
        traceback.print_exc()
        return

    print("\nToutes les tâches de génération de clips ont été lancées.")
    return "OK"