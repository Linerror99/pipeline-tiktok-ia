import functions_framework
from google.cloud import storage, firestore
import google.auth
from google.auth.transport.requests import Request
import requests
import os
import re
import time
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()
credentials, project_id = google.auth.default()

def get_access_token():
    """Récupère un token d'accès pour l'API Vertex AI"""
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token

def extract_video_scenes(script_content):
    """
    Extrait les scènes visuelles du script avec leur INDEX ORIGINAL
    """
    scenes = []
    scene_index = 0
    
    base_style_prompt = "Cinematic, photorealistic, vibrant colors. "
    
    for line in script_content.splitlines():
        upper_line = line.strip().upper()
        marker_pos = upper_line.find("VISUEL")
        
        if marker_pos != -1:
            colon_pos = upper_line.find(":", marker_pos)
            if colon_pos != -1:
                scene_index += 1
                text_part = line.strip()[colon_pos + 1:]
                prompt_text = text_part.strip().replace('*', '').replace('#', '')
                full_prompt = base_style_prompt + prompt_text
                
                scenes.append({
                    'index': scene_index,  # INDEX ORIGINAL
                    'prompt': full_prompt
                })
    
    return scenes

@functions_framework.cloud_event
def generate_video(cloudevent):
    data = cloudevent.data
    bucket_name = data["bucket"]
    audio_file_name = data["name"]

    print(f"🎬 Déclencheur reçu pour le fichier audio : {audio_file_name}")

    if not audio_file_name.startswith("audio_") or not audio_file_name.endswith(".mp3"):
        print(f"❌ Fichier non-audio {audio_file_name}. Traitement ignoré.")
        return "OK"

    # --- Lecture du script ---
    script_file_name = audio_file_name.replace("audio_", "script_").replace(".mp3", ".txt")
    try:
        bucket = storage_client.bucket(bucket_name)
        script_blob = bucket.blob(script_file_name)
        if not script_blob.exists():
            print(f"❌ Erreur: script {script_file_name} non trouvé.")
            return "Error: Script not found"
        script_content = script_blob.download_as_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du script : {e}")
        return

    print(f"📄 Script chargé ({len(script_content)} caractères)")

    # --- Extraction des scènes avec INDEX ORIGINAL ---
    scenes = extract_video_scenes(script_content)

    if not scenes:
        print("❌ Aucun prompt visuel trouvé. Arrêt.")
        return "OK"

    print(f"🎥 {len(scenes)} scènes visuelles détectées")
    
    # Afficher les scènes avec leur index
    for scene in scenes:
        print(f"  Scène {scene['index']}: {scene['prompt'][:60]}...")

    # --- Appel API REST ---
    try:
        video_base_name = os.path.splitext(audio_file_name.replace("audio_", ""))[0]
        location = "us-central1"
        model_id = "veo-3.0-generate-001"
        
        api_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        print(f"🚀 Lancement de {len(scenes)} tâches Veo en parallèle...")
        
        # Préparer le document video_status centralisé
        clips_data = {}
        
        for scene in scenes:
            scene_index = scene['index']  # INDEX ORIGINAL (pas l'ordre de la boucle)
            prompt = scene['prompt']
            
            # IMPORTANT : Utiliser scene_index (pas enumerate)
            output_storage_uri = f"gs://{bucket_name}/video_clips/{video_base_name}/clip_{scene_index}/"
            
            print(f"  🎬 Lancement Scène {scene_index}")
            print(f"     Sortie : {output_storage_uri}")

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

            response = requests.post(api_endpoint, headers=headers, json=request_body)
            
            if response.status_code == 200:
                operation_data = response.json()
                operation_name = operation_data.get('name', 'N/A')
                print(f"    ✓ Tâche lancée pour Scène {scene_index}")
                print(f"      Opération : {operation_name}")
                
                # Enregistrer dans le dictionnaire
                clips_data[str(scene_index)] = {
                    'status': 'pending',
                    'operation_name': operation_name,
                    'prompt': prompt,
                    'retry_count': 0,
                    'gcs_uri': None
                }
            else:
                print(f"    ❌ Erreur API pour Scène {scene_index} (code {response.status_code})")
                print(f"       {response.text}")
                
                # Enregistrer l'échec
                clips_data[str(scene_index)] = {
                    'status': 'failed',
                    'operation_name': None,
                    'prompt': prompt,
                    'retry_count': 0,
                    'gcs_uri': None,
                    'error': response.text[:200]
                }
        
        # Créer le document video_status centralisé dans Firestore
        video_status_ref = firestore_client.collection('video_status').document(video_base_name)
        video_status_ref.set({
            'video_id': video_base_name,
            'total_clips': len(scenes),
            'completed_clips': 0,
            'status': 'processing',  # processing, ready_to_assemble, assembling, completed, failed
            'clips': clips_data,
            'bucket_name': bucket_name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        print(f"\n📝 Document video_status créé pour {video_base_name}")
        print(f"   Total clips: {len(scenes)}")
        print(f"   Status: processing")
            
    except Exception as e:
        print(f"❌ Erreur lors du lancement de la génération vidéo : {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n🎉 Toutes les tâches lancées avec ORDRE PRÉSERVÉ !")
    return "OK"