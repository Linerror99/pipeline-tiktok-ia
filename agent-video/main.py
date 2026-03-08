import functions_framework
from google.cloud import storage, firestore
from google import genai
from google.genai import types
import os
import json
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()

PROJECT_ID = os.environ.get("GCP_PROJECT", "pipeline-video-ia")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# Client Gemini API pour Veo 3.1 via Vertex AI
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

@functions_framework.cloud_event
def generate_video_v2(cloudevent):
    """
    Cloud Function déclenchée par upload de script_v2.json
    Génère BLOC 1 (8s) avec Veo 3.1 Fast + audio natif
    
    CloudEvent data:
    {
        "bucket": "tiktok-pipeline-v2-artifacts",
        "name": "{video_id}/script_v2.json"
    }
    """
    try:
        data = cloudevent.data
        bucket_name = data["bucket"]
        file_name = data["name"]
        
        print(f"📡 Déclencheur reçu pour le fichier : {file_name}")
        
        # Vérifier que c'est bien un script_v2.json
        if not file_name.endswith("/script_v2.json"):
            print(f"⚠️ Fichier non-script {file_name}. Traitement ignoré.")
            return "OK"
        
        # Extraire video_id du path: {video_id}/script_v2.json
        video_id = file_name.split("/")[0]
        
        print(f"🎬 Génération Veo 3.1 Fast pour video_id: {video_id}")
        
    except Exception as e:
        print(f"❌ Erreur parsing CloudEvent: {e}")
        return "ERROR"
    
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
        
        # Générer TOUS les blocs en parallèle
        print(f"\n{'='*60}")
        print(f"🎬 GÉNÉRATION DE {len(blocks)} BLOCS EN PARALLÈLE")
        print(f"{'='*60}")
        
        operations = {}
        clips_status = {}
        
        for idx, block_data in enumerate(blocks, start=1):
            print(f"\n🎥 BLOC {idx}/{len(blocks)}")
            print(f"   Dialogue: {block_data['dialogue'][:80]}...")
            print(f"   Durée: {block_data['duration']}s")
            
            # Construire prompt avec contexte de continuité si bloc > 1
            visual_prompt = block_data['visuel']
            dialogue = block_data['dialogue']
            
            if idx > 1:
                # Ajouter contexte pour continuité narrative
                full_prompt = f"Suite de la scène précédente. {visual_prompt}\n\nDialogue à générer en audio: \"{dialogue}\""
            else:
                full_prompt = f"{visual_prompt}\n\nDialogue à générer en audio: \"{dialogue}\""
            
            # Générer avec Veo 3.1 (avec gestion des erreurs de safety)
            try:
                operation = genai_client.models.generate_videos(
                    model="veo-3.1-generate-001",
                    prompt=full_prompt,
                    config=types.GenerateVideosConfig(
                        aspect_ratio="9:16",
                        resolution="720p",
                        duration_seconds=8,
                        person_generation="allow_all"
                    )
                )
                
                operations[idx] = operation.name
                clips_status[idx] = 'generating'
                
                print(f"   ✅ Génération lancée: {operation.name[:60]}...")
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Bloc {idx} échoué: {error_msg}")
                
                # Si erreur de safety/guidelines, générer prompt générique de secours
                if 'usage guidelines' in error_msg.lower() or 'third-party content' in error_msg.lower():
                    print(f"   🔄 Tentative avec prompt générique...")
                    fallback_prompt = f"Scène abstraite colorée avec des formes géométriques en mouvement sur fond uni. Style moderne et épuré. Durée: 8 secondes."
                    
                    try:
                        operation = genai_client.models.generate_videos(
                            model="veo-3.1-generate-001",
                            prompt=fallback_prompt,
                            config=types.GenerateVideosConfig(
                                aspect_ratio="9:16",
                                resolution="720p",
                                duration_seconds=8,
                                person_generation="allow_all"
                            )
                        )
                        operations[idx] = operation.name
                        clips_status[idx] = 'generating'
                        print(f"   ✅ Prompt de secours accepté")
                    except Exception as e2:
                        print(f"   ❌ Échec définitif bloc {idx}: {e2}")
                        clips_status[idx] = 'failed'
                else:
                    clips_status[idx] = 'failed'
        
        print(f"\n✅ {len(blocks)} générations lancées en parallèle !")
        
        # Convertir les clés int en string pour Firestore
        operations_str = {str(k): v for k, v in operations.items()}
        clips_status_str = {str(k): v for k, v in clips_status.items()}
        
        # Stocker dans Firestore pour monitoring
        firestore_client.collection('v2_veo_operations').document(video_id).set({
            'video_id': video_id,
            'script_file': f"{video_id}/script_v2.json",
            'operations': operations_str,  # Dict {"1": "op_name", "2": "op_name", ...}
            'clips_status': clips_status_str,  # Dict {"1": "generating", "2": "generating", ...}
            'status': 'generating_parallel',
            'total_blocks': len(blocks),
            'completed_blocks': 0,
            'blocks': blocks,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'retry_count': 0
        })
        
        # Update v2_video_status
        firestore_client.collection('v2_video_status').document(video_id).update({
            'status': 'generating_video',
            'current_step': 'parallel_generation',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        print(f"📊 Firestore updated: v2_veo_operations/{video_id}")
        
        return {
            "status": "success",
            "video_id": video_id,
            "operations_count": len(operations),
            "total_blocks": len(blocks),
            "message": f"Génération de {len(blocks)} blocs lancée en parallèle"
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