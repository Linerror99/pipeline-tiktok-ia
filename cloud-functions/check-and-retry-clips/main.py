"""
Cloud Function pour vérifier et relancer les clips vidéo qui ont échoué ou sont bloqués
Déclenchée par Cloud Scheduler toutes les 10 minutes
"""
import functions_framework
from google.cloud import storage, firestore
import google.auth
from google.auth.transport.requests import Request
import requests
from datetime import datetime, timedelta

storage_client = storage.Client()
firestore_client = firestore.Client()
credentials, project_id = google.auth.default()

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
    Fonction principale qui vérifie toutes les opérations et relance celles qui ont échoué
    """
    print("🔍 Démarrage de la vérification des clips...")
    
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
        'success': success_count,
        'message': f"Vérifié {checked_count} opérations, relancé {retried_count} clips, {success_count} succès"
    }
    
    print(f"✅ {result['message']}")
    return result, 200
