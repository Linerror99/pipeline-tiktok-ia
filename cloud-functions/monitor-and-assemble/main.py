"""
Cloud Function de monitoring et déclenchement de l'assembleur
Vérifie les clips, relance ceux qui échouent, et déclenche l'assembleur quand tous les clips sont prêts
Déclenchée par Cloud Scheduler toutes les 2 minutes
"""
import functions_framework
from google.cloud import storage, firestore
import google.auth
from google.auth.transport.requests import Request
import requests
from datetime import datetime
import os

storage_client = storage.Client()
firestore_client = firestore.Client()
credentials, project_id = google.auth.default()

# URL de l'agent assembleur (à configurer après déploiement)
AGENT_ASSEMBLER_URL = os.environ.get('AGENT_ASSEMBLER_URL', '')

def get_access_token():
    """Récupère un token d'accès pour l'API Vertex AI"""
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token

def check_veo_operation(operation_name, bucket_name, video_id, scene_index):
    """
    Vérifie le statut d'une opération long-running Veo
    Si l'API retourne 404, vérifie directement dans GCS (opération expirée)
    Returns: ('ready'|'pending'|'failed', gcs_uri|None)
    """
    try:
        # Extract location from operation name
        # Format: projects/{project}/locations/{location}/operations/{operation_id}
        parts = operation_name.split('/')
        if len(parts) < 6:
            return 'failed', None
        
        location = parts[3]
        
        api_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/{operation_name}"
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(api_endpoint, headers=headers)
        
        if response.status_code == 200:
            operation_data = response.json()
            
            # Vérifier si l'opération est terminée
            if operation_data.get('done', False):
                # Vérifier s'il y a une erreur
                if 'error' in operation_data:
                    error_msg = operation_data['error'].get('message', 'Unknown error')
                    print(f"      Erreur Veo: {error_msg}")
                    return 'failed', None
                else:
                    # Succès - extraire l'URI GCS
                    result = operation_data.get('response', {})
                    generated_samples = result.get('generatedSamples', [])
                    if generated_samples and len(generated_samples) > 0:
                        gcs_uri = generated_samples[0].get('gcsUri')
                        return 'ready', gcs_uri
                    else:
                        return 'failed', None
            else:
                # Opération encore en cours
                return 'pending', None
        
        elif response.status_code == 404:
            # L'opération a expiré de l'API (après ~1h)
            # Vérifier directement dans GCS si le fichier existe
            print(f"      ⚠️ Opération expirée (404), vérification GCS...")
            
            bucket = storage_client.bucket(bucket_name)
            clip_prefix = f"video_clips/{video_id}/clip_{scene_index}/"
            blobs = list(bucket.list_blobs(prefix=clip_prefix))
            
            # Chercher un fichier .mp4
            mp4_files = [b for b in blobs if b.name.endswith('.mp4')]
            
            if mp4_files:
                # Fichier trouvé dans GCS !
                gcs_uri = f"gs://{bucket_name}/{mp4_files[0].name}"
                print(f"      ✅ Clip trouvé dans GCS: {gcs_uri}")
                return 'ready', gcs_uri
            else:
                # Pas de fichier dans GCS, considérer comme échoué
                print(f"      ❌ Aucun clip dans GCS")
                return 'failed', None
        
        else:
            print(f"      ⚠️ Erreur API status check: {response.status_code}")
            return 'failed', None
            
    except Exception as e:
        print(f"      ⚠️ Erreur check operation: {e}")
        return 'failed', None

def retry_clip(video_id, scene_index, prompt, bucket_name):
    """
    Relance la génération d'un clip qui a échoué
    Returns: (operation_name|None, status)
    """
    try:
        print(f"    🔄 Retry clip {scene_index}")
        
        location = "us-central1"
        model_id = "veo-3.0-generate-001"
        output_storage_uri = f"gs://{bucket_name}/video_clips/{video_id}/clip_{scene_index}/"
        
        api_endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predictLongRunning"
        
        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
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
            operation_name = operation_data.get('name', None)
            print(f"      ✓ Retry lancé: {operation_name}")
            return operation_name, 'pending'
        else:
            print(f"      ❌ Retry échoué: {response.status_code}")
            print(f"         {response.text[:200]}")
            return None, 'failed'
            
    except Exception as e:
        print(f"      ❌ Erreur retry: {e}")
        return None, 'failed'

def trigger_assembler(video_id):
    """
    Déclenche l'agent assembleur via HTTP
    """
    try:
        if not AGENT_ASSEMBLER_URL:
            print(f"    ⚠️ AGENT_ASSEMBLER_URL non configurée")
            return False
        
        print(f"    📞 Appel de l'assembleur: {AGENT_ASSEMBLER_URL}")
        
        response = requests.post(
            AGENT_ASSEMBLER_URL,
            json={"video_id": video_id},
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes pour l'assemblage
        )
        
        if response.status_code == 200:
            print(f"      ✓ Assembleur appelé avec succès")
            return True
        else:
            print(f"      ❌ Erreur assembleur: {response.status_code}")
            print(f"         {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"    ❌ Erreur appel assembleur: {e}")
        return False

@functions_framework.http
def monitor_and_assemble(request):
    """
    Fonction principale qui vérifie tous les clips et déclenche l'assembleur quand prêt
    """
    print("🔍 === Monitoring des vidéos en cours ===\n")
    
    # Récupérer toutes les vidéos en status 'processing'
    videos_ref = firestore_client.collection('video_status')
    processing_videos = videos_ref.where('status', '==', 'processing').stream()
    
    checked_videos = 0
    triggered_assemblies = 0
    
    for video_doc in processing_videos:
        checked_videos += 1
        video_data = video_doc.to_dict()
        video_id = video_data['video_id']
        clips = video_data['clips']
        total_clips = video_data['total_clips']
        bucket_name = video_data.get('bucket_name', f'tiktok-pipeline-artifacts-{project_id}')
        
        print(f"📹 Vidéo: {video_id}")
        print(f"   Total clips: {total_clips}")
        
        completed = 0
        pending = 0
        failed = 0
        needs_update = False
        
        # Vérifier chaque clip
        for clip_idx, clip_data in clips.items():
            status = clip_data['status']
            
            if status == 'pending':
                pending += 1
                # Vérifier l'opération Veo
                operation_name = clip_data.get('operation_name')
                
                if operation_name:
                    new_status, gcs_uri = check_veo_operation(operation_name, bucket_name, video_id, clip_idx)
                    
                    if new_status == 'ready':
                        print(f"   ✓ Clip {clip_idx} prêt")
                        clips[clip_idx]['status'] = 'ready'
                        clips[clip_idx]['gcs_uri'] = gcs_uri
                        needs_update = True
                        completed += 1
                        pending -= 1
                        
                    elif new_status == 'failed':
                        print(f"   ⚠️ Clip {clip_idx} échoué")
                        retry_count = clip_data.get('retry_count', 0)
                        
                        if retry_count < 3:
                            # Relancer
                            new_op, new_stat = retry_clip(
                                video_id, 
                                clip_idx, 
                                clip_data['prompt'],
                                bucket_name
                            )
                            clips[clip_idx]['operation_name'] = new_op
                            clips[clip_idx]['status'] = new_stat
                            clips[clip_idx]['retry_count'] = retry_count + 1
                            needs_update = True
                            
                            if new_stat == 'failed':
                                failed += 1
                                pending -= 1
                        else:
                            # Abandonner après 3 tentatives
                            print(f"      ❌ Abandonné après 3 tentatives")
                            clips[clip_idx]['status'] = 'abandoned'
                            needs_update = True
                            failed += 1
                            pending -= 1
                            
                    # new_status == 'pending' : rien à faire, on attend
                    
            elif status == 'ready':
                completed += 1
                
            elif status == 'abandoned' or status == 'failed':
                failed += 1
        
        print(f"   État: {completed} prêts, {pending} en cours, {failed} échoués")
        
        # Mettre à jour Firestore si nécessaire
        if needs_update:
            video_doc.reference.update({
                'clips': clips,
                'completed_clips': completed,
                'updated_at': datetime.utcnow()
            })
            print(f"   📝 Firestore mis à jour")
        
        # Si tous les clips sont prêts → déclencher l'assembleur
        if completed == total_clips:
            print(f"   🎉 Tous les clips prêts ! Déclenchement de l'assembleur...")
            
            if trigger_assembler(video_id):
                video_doc.reference.update({
                    'status': 'assembling',
                    'updated_at': datetime.utcnow()
                })
                triggered_assemblies += 1
                print(f"   ✅ Assembleur déclenché\n")
            else:
                print(f"   ❌ Échec déclenchement assembleur\n")
        elif completed + failed == total_clips and failed > 0:
            # Tous les clips sont soit prêts soit abandonnés
            print(f"   ⚠️ {failed} clip(s) abandonné(s). Déclenchement de l'assembleur avec clips disponibles...")
            
            if trigger_assembler(video_id):
                video_doc.reference.update({
                    'status': 'assembling_partial',
                    'updated_at': datetime.utcnow()
                })
                triggered_assemblies += 1
                print(f"   ✅ Assembleur déclenché (partiel)\n")
            else:
                print(f"   ❌ Échec déclenchement assembleur\n")
        else:
            print(f"   ⏳ Attente des clips restants...\n")
    
    if checked_videos == 0:
        print("ℹ️ Aucune vidéo en cours de traitement\n")
    
    result = {
        'checked_videos': checked_videos,
        'triggered_assemblies': triggered_assemblies,
        'message': f"Vérifié {checked_videos} vidéo(s), déclenché {triggered_assemblies} assemblage(s)"
    }
    
    print(f"✅ {result['message']}")
    return result, 200
