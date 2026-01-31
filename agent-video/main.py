import functions_framework
from google.cloud import storage, firestore, aiplatform
from google.cloud.aiplatform_v1beta1 import types as aiplatform_types
import os
import json
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()

PROJECT_ID = os.environ.get("GCP_PROJECT", "pipeline-video-ia")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# Initialiser Vertex AI
aiplatform.init(project=PROJECT_ID, location=LOCATION)

@functions_framework.http
def generate_video_v2(request):
    """
    Cloud Function HTTP pour générer vidéo V2 avec Veo 3.1 Fast
    
    Génère uniquement BLOC 1 (8s) avec audio natif
    Les extensions (blocs 2+) sont gérées par monitor-veo31
    
    Request JSON:
    {
        "video_id": "xxx",
        "script_path": "gs://bucket/video_id/script_v2.json"  # optionnel
    }
    """
    request_json = request.get_json(silent=True)
    
    if not request_json or "video_id" not in request_json:
        return {"error": "video_id manquant"}, 400
    
    video_id = request_json["video_id"]
    
    print(f"🎬 Génération Veo 3.1 Fast pour video_id: {video_id}")
    
    try:
        # Charger script V2
        bucket = storage_client.bucket(BUCKET_NAME)
        script_blob = bucket.blob(f"{video_id}/script_v2.json")
        
        if not script_blob.exists():
            return {"error": f"Script {video_id}/script_v2.json non trouvé"}, 404
        
        script_data = json.loads(script_blob.download_as_text())
        blocks = script_data.get('blocks', [])
        
        if not blocks:
            return {"error": "Aucun bloc dans le script"}, 400
        
        print(f"📝 Script chargé: {len(blocks)} blocs")
        
        # Générer BLOC 1 uniquement (8s) avec audio natif
        bloc_1 = blocks[0]
        
        # Construire prompt avec dialogue pour audio natif
        visual_prompt = bloc_1['visuel']
        dialogue = bloc_1['dialogue']
        
        # Prompt complet: visuel + audio
        full_prompt = f"{visual_prompt}\n\nDialogue à générer en audio: \"{dialogue}\""
        
        print(f"🎯 BLOC 1 (8s):")
        print(f"   Visuel: {visual_prompt[:60]}...")
        print(f"   Dialogue: {dialogue[:60]}...")
        
        # Appel Veo 3.1 Fast avec audio natif
        model = aiplatform.preview.GenerativeModel("veo-3.1-fast")
        
        operation = model.generate_videos(
            prompt=full_prompt,
            config=aiplatform_types.GenerateVideosConfig(
                duration_seconds=8,
                resolution="720p",  # Cohérent avec extensions
                aspect_ratio="9:16",
                generate_audio=True,  # Audio natif !
                sample_count=1
            )
        )
        
        print(f"✅ Opération Veo lancée: {operation.name}")
        
        # Enregistrer dans Firestore v2_veo_operations pour monitoring async
        firestore_client.collection('v2_veo_operations').document(video_id).set({
            'video_id': video_id,
            'status': 'generating_block_1',
            'operation_name': operation.name,
            'blocks': blocks,
            'current_block': 1,
            'total_blocks': len(blocks),
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'veo_version': '3.1-fast',
            'retry_count': 0
        })
        
        # Update v2_video_status
        firestore_client.collection('v2_video_status').document(video_id).update({
            'status': 'generating_video',
            'current_step': 'bloc_1_generation',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        print(f"📊 Firestore updated: v2_veo_operations/{video_id}")
        
        return {
            "status": "success",
            "video_id": video_id,
            "operation_name": operation.name,
            "current_block": 1,
            "total_blocks": len(blocks),
            "message": f"Génération BLOC 1 lancée (async)"
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        # Update Firestore avec erreur
        try:
            firestore_client.collection('v2_video_status').document(video_id).update({
                'status': 'error',
                'error_message': str(e),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
        except:
            pass
        
        return {"error": str(e)}, 500