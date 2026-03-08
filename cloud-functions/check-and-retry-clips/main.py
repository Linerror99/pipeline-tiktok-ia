"""
Cloud Function pour vérifier et relancer les clips vidéo qui ont échoué ou sont bloqués
Compatible V1 (Veo 3.0) et V2 (Veo 3.1 génération parallèle)
Déclenchée par Cloud Scheduler toutes les minutes
"""
import functions_framework
from google.cloud import storage, firestore
import google.auth
from google.auth.transport.requests import Request
import requests
from datetime import datetime, timedelta
from google import genai
from google.genai import types
import os

storage_client = storage.Client()
firestore_client = firestore.Client()
credentials, project_id = google.auth.default()

# Client Gemini API pour Veo 3.1 (V2)
genai_client = genai.Client(vertexai=True, project=project_id, location="us-central1")

BUCKET_NAME_V2 = os.environ.get("BUCKET_NAME_V2", "tiktok-pipeline-v2-artifacts")
AGENT_ASSEMBLER_URL = os.environ.get("AGENT_ASSEMBLER_URL", "")

def get_access_token():
    """Récupère un token d'accès pour l'API Vertex AI"""
    if not credentials.valid:
        credentials.refresh(Request())
    return credentials.token

def check_operation_status(operation_name):
    """
    Vérifie le statut d'une opération long-running Veo
    Returns: 'pending', 'success', 'failed'
    """
    try:
        # Extract location from operation name
        # Format: projects/{project}/locations/{location}/operations/{operation_id}
        parts = operation_name.split('/')
        if len(parts) < 6:
            return 'failed'
        
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
                    return 'failed'
                else:
                    return 'success'
            else:
                return 'pending'
        else:
            print(f"⚠️ Erreur API status check: {response.status_code}")
            return 'unknown'
    except Exception as e:
        print(f"⚠️ Erreur check operation: {e}")
        return 'unknown'

def retry_failed_clip(doc_data):
    """
    Relance la génération d'un clip qui a échoué
    """
    try:
        video_id = doc_data['video_id']
        scene_index = doc_data['scene_index']
        prompt = doc_data['prompt']
        bucket_name = f"tiktok-pipeline-artifacts-{project_id}"
        
        print(f"🔄 Retry clip {scene_index} pour vidéo {video_id}")
        
        location = "us-central1"
        model_id = "veo-3.1-generate-001"
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
            operation_name = operation_data.get('name', 'N/A')
            print(f"  ✓ Retry réussi: {operation_name}")
            return operation_name, 'pending'
        else:
            print(f"  ❌ Retry échoué: {response.status_code}")
            return None, 'failed'
            
    except Exception as e:
        print(f"❌ Erreur retry: {e}")
        return None, 'failed'

@functions_framework.http
def check_and_retry_clips(request):
    """
    Fonction principale qui vérifie les opérations V2 (génération parallèle)
    V1 désactivé - migration vers V2 uniquement
    """
    print("🔍 Démarrage de la vérification des clips (V2 uniquement)...")
    
    # === V1 : Désactivé (migration vers V2) ===
    # v1_result = check_v1_operations()
    v1_result = {'checked': 0, 'retried': 0, 'status': 'disabled'}
    
    # === V2 : Génération parallèle ===
    v2_result = check_v2_parallel_operations()
    
    result = {
        'v1': v1_result,
        'v2': v2_result,
        'total_checked': v2_result['checked'],
        'total_retried': v2_result['retried']
    }
    
    print(f"\n✅ Total: {result['total_checked']} vérifiés, {result['total_retried']} relancés")
    return result, 200


def check_v1_operations():
    """Vérifie les opérations V1 (Veo 3.0)"""
    print("\n📹 V1: Vérification opérations individuelles...")
    
    # Récupérer toutes les opérations pending ou failed (avec retry_count < 3)
    operations_ref = firestore_client.collection('video_operations')
    
    # Opérations pending de plus de 15 minutes (probablement bloquées)
    timeout_threshold = datetime.utcnow() - timedelta(minutes=15)
    pending_ops = operations_ref.where('status', '==', 'pending').where('updated_at', '<', timeout_threshold).limit(50).stream()
    
    # Opérations failed avec retry_count < 3
    failed_ops = operations_ref.where('status', '==', 'failed').where('retry_count', '<', 3).limit(50).stream()
    
    checked_count = 0
    retried_count = 0
    success_count = 0
    
    # Vérifier les opérations pending
    for doc in pending_ops:
        doc_data = doc.to_dict()
        operation_name = doc_data.get('operation_name')
        
        if operation_name and operation_name != 'failed':
            checked_count += 1
            status = check_operation_status(operation_name)
            
            print(f"  Clip {doc_data['scene_index']} (vidéo {doc_data['video_id']}): {status}")
            
            if status == 'success':
                # Marquer comme succès
                doc.reference.update({
                    'status': 'success',
                    'updated_at': datetime.utcnow()
                })
                success_count += 1
                print(f"    ✓ Marqué comme succès")
                
            elif status == 'failed':
                # Relancer
                retry_count = doc_data.get('retry_count', 0)
                if retry_count < 3:
                    new_operation, new_status = retry_failed_clip(doc_data)
                    doc.reference.update({
                        'operation_name': new_operation or 'failed',
                        'status': new_status,
                        'retry_count': retry_count + 1,
                        'updated_at': datetime.utcnow()
                    })
                    retried_count += 1
                else:
                    # Trop de retries, abandonner
                    doc.reference.update({
                        'status': 'abandoned',
                        'updated_at': datetime.utcnow()
                    })
                    print(f"    ⚠️ Abandonné après 3 tentatives")
    
    # Relancer les opérations failed
    for doc in failed_ops:
        doc_data = doc.to_dict()
        retry_count = doc_data.get('retry_count', 0)
        
        if retry_count < 3:
            new_operation, new_status = retry_failed_clip(doc_data)
            doc.reference.update({
                'operation_name': new_operation or 'failed',
                'status': new_status,
                'retry_count': retry_count + 1,
                'updated_at': datetime.utcnow()
            })
            retried_count += 1
    
    result = {
        'checked': checked_count,
        'retried': retried_count,
        'success': success_count
    }
    
    print(f"  ✅ V1: {checked_count} vérifiés, {retried_count} relancés, {success_count} succès")
    return result


def check_v2_parallel_operations():
    """Vérifie les opérations V2 (Veo 3.1 génération parallèle)"""
    print("\n🎬 V2: Vérification génération parallèle...")
    
    # Chercher les vidéos en cours de génération ET prêtes pour assemblage
    generating_ops = firestore_client.collection('v2_veo_operations')\
        .where('status', '==', 'generating_parallel')\
        .stream()
    
    ready_ops = firestore_client.collection('v2_veo_operations')\
        .where('status', '==', 'ready_for_assembly')\
        .stream()
    
    operations_list = list(generating_ops) + list(ready_ops)
    
    if len(operations_list) == 0:
        print("  ✅ Aucune opération V2 en cours")
        return {'checked': 0, 'retried': 0, 'success': 0, 'assembled': 0}
    
    checked_count = 0
    success_count = 0
    assembled_count = 0
    
    for op_doc in operations_list:
        op_data = op_doc.to_dict()
        video_id = op_doc.id
        current_status = op_data.get('status')
        
        # Si déjà ready_for_assembly, appeler directement l'assembleur
        if current_status == 'ready_for_assembly':
            print(f"  🎬 {video_id}: Prêt pour assemblage → Appel assembler")
            trigger_v2_assembly(video_id)
            assembled_count += 1
            checked_count += 1
            continue
        
        operations_dict = op_data.get('operations', {})
        clips_status = op_data.get('clips_status', {})
        completed_blocks = op_data.get('completed_blocks', 0)
        total_blocks = op_data.get('total_blocks', 0)
        
        print(f"  🎬 {video_id}: {completed_blocks}/{total_blocks} blocs terminés")
        
        blocks_completed_this_run = 0
        
        # Vérifier chaque opération
        for block_idx, operation_name in operations_dict.items():
            block_num = int(block_idx)
            current_status = clips_status.get(block_idx, 'unknown')
            
            # Skip si déjà terminé
            if current_status == 'completed':
                continue
            
            checked_count += 1
            
            try:
                # Récupérer status via SDK
                operation = types.GenerateVideosOperation(name=operation_name)
                operation = genai_client.operations.get(operation)
                
                done = operation.done if hasattr(operation, 'done') else False
                
                if done:
                    # Vérifier si erreur
                    if hasattr(operation, 'error') and operation.error:
                        print(f"    ❌ Bloc {block_num} échoué: {operation.error}")
                        clips_status[block_idx] = 'failed'
                    else:
                        print(f"    ✅ Bloc {block_num} terminé !")
                        # Télécharger le bloc
                        download_v2_block(video_id, block_num, operation)
                        clips_status[block_idx] = 'completed'
                        blocks_completed_this_run += 1
                        success_count += 1
                        
            except Exception as e:
                print(f"    ❌ Erreur bloc {block_num}: {e}")
                clips_status[block_idx] = 'error'
        
        # Mettre à jour Firestore
        if blocks_completed_this_run > 0:
            new_completed = completed_blocks + blocks_completed_this_run
            
            firestore_client.collection('v2_veo_operations').document(video_id).update({
                'clips_status': clips_status,
                'completed_blocks': new_completed,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            # Si tous terminés → Déclencher assemblage
            if new_completed >= total_blocks:
                print(f"    🎉 Tous les blocs terminés → Assemblage")
                trigger_v2_assembly(video_id)
                assembled_count += 1
    
    result = {
        'checked': checked_count,
        'retried': 0,
        'success': success_count,
        'assembled': assembled_count
    }
    
    print(f"  ✅ V2: {checked_count} blocs vérifiés, {success_count} terminés, {assembled_count} assemblés")
    return result


def download_v2_block(video_id, block_num, operation):
    """Télécharge un bloc V2 terminé"""
    try:
        if not hasattr(operation, 'response') or not operation.response:
            raise Exception("Pas de réponse")
        
        response = operation.response
        
        if not hasattr(response, 'generated_videos') or not response.generated_videos:
            raise Exception("Aucune vidéo")
        
        generated_video = response.generated_videos[0]
        
        if not hasattr(generated_video, 'video') or not generated_video.video:
            raise Exception("Pas de fichier vidéo")
        
        video_file = generated_video.video
        
        # Télécharger
        local_path = f'/tmp/{video_id}_block_{block_num}.mp4'
        
        if hasattr(video_file, 'video_bytes') and video_file.video_bytes:
            with open(local_path, 'wb') as f:
                f.write(video_file.video_bytes)
            
            # Upload vers GCS
            bucket = storage_client.bucket(BUCKET_NAME_V2)
            video_blob = bucket.blob(f'{video_id}/block_{block_num}.mp4')
            video_blob.upload_from_filename(local_path)
            os.remove(local_path)
            
            print(f"      ✅ Bloc {block_num} sauvegardé ({len(video_file.video_bytes)} octets)")
        else:
            raise Exception("Impossible d'accéder aux video_bytes")
        
    except Exception as e:
        print(f"      ❌ Erreur téléchargement bloc {block_num}: {e}")
        raise


def trigger_v2_assembly(video_id):
    """Déclenche l'assemblage V2"""
    try:
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': 'ready_for_assembly',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        firestore_client.collection('v2_video_status').document(video_id).update({
            'status': 'assembling',
            'current_step': 'assembly',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        # Appeler agent-assembler si URL disponible
        if AGENT_ASSEMBLER_URL:
            try:
                response = requests.post(
                    AGENT_ASSEMBLER_URL,
                    json={'video_id': video_id},
                    timeout=10
                )
                print(f"      ✅ Assembler appelé: {response.status_code}")
            except Exception as http_err:
                print(f"      ⚠️ Erreur appel assembler: {http_err}")
        
    except Exception as e:
        print(f"      ❌ Erreur déclenchement assemblage: {e}")
