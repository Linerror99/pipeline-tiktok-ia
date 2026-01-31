"""
Cloud Function V2: Monitoring opérations Veo 3.1 et extensions
Vérifie les opérations en cours, télécharge les blocs terminés,
lance les extensions (blocs suivants) et déclenche l'assemblage final

Déclenchée par Cloud Scheduler toutes les minutes
"""
import functions_framework
from google.cloud import storage, firestore, aiplatform
from google.cloud.aiplatform_v1beta1 import types as aiplatform_types
import os
import requests
import urllib.request
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()

PROJECT_ID = os.environ.get("GCP_PROJECT", "pipeline-video-ia")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME")
AGENT_ASSEMBLER_URL = os.environ.get("AGENT_ASSEMBLER_URL", "")

# Initialiser Vertex AI
aiplatform.init(project=PROJECT_ID, location=LOCATION)

@functions_framework.http
def monitor_veo31_operations(request):
    """
    Vérifie toutes les opérations Veo 3.1 en cours
    Appelé par Cloud Scheduler chaque minute
    """
    print("=" * 70)
    print("🔍 Monitor Veo 3.1 - Vérification opérations")
    print("=" * 70)
    
    # Récupérer opérations en cours
    operations = firestore_client.collection('v2_veo_operations')\
        .where('status', 'in', [
            'generating_block_1', 
            'generating_block_2', 
            'generating_block_3',
            'generating_block_4',
            'generating_block_5',
            'generating_block_6',
            'generating_block_7',
            'generating_block_8',
            'generating_block_9',
            'generating_block_10'
        ])\
        .stream()
    
    operations_list = list(operations)
    print(f"📊 {len(operations_list)} opérations en cours\n")
    
    if len(operations_list) == 0:
        print("✅ Aucune opération en cours")
        return {"status": "ok", "checked": 0}, 200
    
    processed_count = 0
    
    for op_doc in operations_list:
        op_data = op_doc.to_dict()
        video_id = op_doc.id
        
        try:
            print(f"🎬 {video_id}")
            print(f"   Status: {op_data['status']}")
            print(f"   Bloc: {op_data['current_block']}/{op_data['total_blocks']}")
            
            # Vérifier status operation
            operation_name = op_data['operation_name']
            operation = aiplatform.Operation(operation_name)
            
            if operation.done:
                if operation.error:
                    print(f"   ❌ Erreur: {operation.error.message}")
                    handle_veo_failure(video_id, op_data, operation.error.message)
                else:
                    print(f"   ✅ Terminé !")
                    handle_veo_success(video_id, op_data, operation)
                
                processed_count += 1
            else:
                print(f"   ⏳ En cours...")
                
        except Exception as e:
            print(f"   ❌ Erreur monitoring: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"✅ Monitor terminé: {processed_count} opérations traitées")
    print("=" * 70)
    
    return {
        "status": "ok",
        "checked": len(operations_list),
        "processed": processed_count
    }, 200


def handle_veo_success(video_id, op_data, operation):
    """Opération réussie → Télécharger et lancer bloc suivant ou assembler"""
    
    current_block = op_data['current_block']
    total_blocks = op_data['total_blocks']
    blocks = op_data['blocks']
    
    print(f"\n   📥 Traitement bloc {current_block}...")
    
    try:
        # Récupérer la vidéo générée
        result = operation.result
        
        if not result.generated_videos:
            print(f"   ❌ Aucune vidéo générée")
            handle_veo_failure(video_id, op_data, "Aucune vidéo générée")
            return
        
        video_uri = result.generated_videos[0].video.uri
        print(f"   📍 URI vidéo: {video_uri}")
        
        # Télécharger la vidéo
        bucket = storage_client.bucket(BUCKET_NAME)
        video_blob = bucket.blob(f'{video_id}/block_{current_block}.mp4')
        
        # Download depuis URI Vertex AI
        local_path = f'/tmp/{video_id}_block_{current_block}.mp4'
        urllib.request.urlretrieve(video_uri, local_path)
        
        # Upload vers Cloud Storage
        video_blob.upload_from_filename(local_path)
        
        # Nettoyer fichier local
        os.remove(local_path)
        
        print(f"   ✅ Bloc {current_block} sauvegardé: gs://{BUCKET_NAME}/{video_id}/block_{current_block}.mp4")
        
        # Si blocs restants → Lancer extension
        if current_block < total_blocks:
            next_block = current_block + 1
            launch_extension(video_id, op_data, next_block, video_uri)
        else:
            # Tous blocs terminés → Déclencher assemblage
            print(f"\n   🎉 Tous les blocs terminés ({total_blocks}/{total_blocks})")
            trigger_assembly(video_id)
            
    except Exception as e:
        print(f"   ❌ Erreur traitement succès: {e}")
        import traceback
        traceback.print_exc()
        handle_veo_failure(video_id, op_data, str(e))


def launch_extension(video_id, op_data, next_block, previous_video_uri):
    """Lance la génération du bloc suivant (extension)"""
    
    blocks = op_data['blocks']
    block_data = blocks[next_block - 1]  # Index 0-based
    
    print(f"\n   🔄 Lancement extension BLOC {next_block}...")
    print(f"      Dialogue: {block_data['dialogue'][:50]}...")
    print(f"      Durée: {block_data['duration']}s")
    
    try:
        # Construire prompt
        visual_prompt = block_data['visuel']
        dialogue = block_data['dialogue']
        full_prompt = f"{visual_prompt}\n\nDialogue à générer en audio: \"{dialogue}\""
        
        # Générer extension
        model = aiplatform.preview.GenerativeModel("veo-3.1-fast")
        
        operation = model.generate_videos(
            prompt=full_prompt,
            video=aiplatform_types.Video(uri=previous_video_uri),  # Extension depuis vidéo précédente
            config=aiplatform_types.GenerateVideosConfig(
                duration_seconds=7,  # Extensions = 7s
                resolution="720p",
                aspect_ratio="9:16",
                generate_audio=True,
                sample_count=1
            )
        )
        
        print(f"   ✅ Extension lancée: {operation.name}")
        
        # Update Firestore
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': f'generating_block_{next_block}',
            'operation_name': operation.name,
            'current_block': next_block,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        firestore_client.collection('v2_video_status').document(video_id).update({
            'current_step': f'bloc_{next_block}_generation',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        print(f"   📊 Firestore updated: bloc {next_block}")
        
    except Exception as e:
        print(f"   ❌ Erreur lancement extension: {e}")
        import traceback
        traceback.print_exc()
        handle_veo_failure(video_id, op_data, f"Erreur extension bloc {next_block}: {e}")


def trigger_assembly(video_id):
    """Déclenche l'assemblage final de tous les blocs"""
    
    print(f"\n   🎬 Déclenchement assemblage...")
    
    try:
        # Update Firestore
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': 'ready_for_assembly',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        firestore_client.collection('v2_video_status').document(video_id).update({
            'status': 'assembling',
            'current_step': 'assembly',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        # Appeler agent-assembler V2
        if AGENT_ASSEMBLER_URL:
            response = requests.post(
                AGENT_ASSEMBLER_URL,
                json={'video_id': video_id},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ Assembleur appelé avec succès")
            else:
                print(f"   ⚠️ Erreur appel assembleur: {response.status_code}")
        else:
            print(f"   ⚠️ AGENT_ASSEMBLER_URL non configuré")
        
    except Exception as e:
        print(f"   ❌ Erreur déclenchement assemblage: {e}")
        import traceback
        traceback.print_exc()


def handle_veo_failure(video_id, op_data, error_message):
    """Gestion échecs avec retry"""
    
    retry_count = op_data.get('retry_count', 0)
    current_block = op_data['current_block']
    
    print(f"\n   ⚠️ Échec bloc {current_block} (retry {retry_count}/3)")
    print(f"      Erreur: {error_message}")
    
    if retry_count < 3:
        # Retry
        print(f"   🔄 Retry {retry_count+1}/3...")
        
        try:
            blocks = op_data['blocks']
            block_data = blocks[current_block - 1]
            
            # Reconstruire prompt
            visual_prompt = block_data['visuel']
            dialogue = block_data['dialogue']
            full_prompt = f"{visual_prompt}\n\nDialogue à générer en audio: \"{dialogue}\""
            
            # Relancer génération
            model = aiplatform.preview.GenerativeModel("veo-3.1-fast")
            
            # Si bloc 1, pas de vidéo source
            if current_block == 1:
                operation = model.generate_videos(
                    prompt=full_prompt,
                    config=aiplatform_types.GenerateVideosConfig(
                        duration_seconds=8,
                        resolution="720p",
                        aspect_ratio="9:16",
                        generate_audio=True,
                        sample_count=1
                    )
                )
            else:
                # Extension - récupérer vidéo précédente
                bucket = storage_client.bucket(BUCKET_NAME)
                prev_blob = bucket.blob(f'{video_id}/block_{current_block-1}.mp4')
                
                if prev_blob.exists():
                    prev_uri = f"gs://{BUCKET_NAME}/{video_id}/block_{current_block-1}.mp4"
                    
                    operation = model.generate_videos(
                        prompt=full_prompt,
                        video=aiplatform_types.Video(uri=prev_uri),
                        config=aiplatform_types.GenerateVideosConfig(
                            duration_seconds=7,
                            resolution="720p",
                            aspect_ratio="9:16",
                            generate_audio=True,
                            sample_count=1
                        )
                    )
                else:
                    raise Exception(f"Bloc précédent {current_block-1} non trouvé")
            
            # Update Firestore
            firestore_client.collection('v2_veo_operations').document(video_id).update({
                'operation_name': operation.name,
                'retry_count': retry_count + 1,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            print(f"   ✅ Retry lancé: {operation.name}")
            
        except Exception as e:
            print(f"   ❌ Erreur retry: {e}")
            mark_as_failed(video_id, error_message)
    else:
        # Échec définitif après 3 tentatives
        print(f"   ❌ Échec définitif après 3 tentatives")
        mark_as_failed(video_id, error_message)


def mark_as_failed(video_id, error_message):
    """Marque la vidéo comme échouée"""
    
    firestore_client.collection('v2_veo_operations').document(video_id).update({
        'status': 'failed',
        'error_message': error_message,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    
    firestore_client.collection('v2_video_status').document(video_id).update({
        'status': 'error',
        'error_message': f'Génération Veo échouée: {error_message}',
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    
    print(f"   📊 Vidéo {video_id} marquée comme échouée")
