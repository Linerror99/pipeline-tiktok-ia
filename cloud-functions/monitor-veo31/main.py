"""
Cloud Function V2: Monitoring opérations Veo 3.1 et extensions
Vérifie les opérations en cours, télécharge les blocs terminés,
lance les extensions (blocs suivants) et déclenche l'assemblage final

Déclenchée par Cloud Scheduler toutes les minutes
"""
import functions_framework
from google.cloud import storage, firestore
from google import genai
from google.genai import types
from google.auth.transport.requests import Request
from google.auth import default
import os
import requests
import urllib.request
import time
import json
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()

PROJECT_ID = os.environ.get("GCP_PROJECT", "pipeline-video-ia")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME")
AGENT_ASSEMBLER_URL = os.environ.get("AGENT_ASSEMBLER_URL", "")

# Client Gemini API pour Veo 3.1 via Vertex AI
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

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
            
            print(f"   🔍 Operation: {operation_name[:100]}...")
            
            # Créer objet operation depuis le nom stocké
            # Selon la documentation Veo 3.1 officielle
            try:
                operation = types.GenerateVideosOperation(name=operation_name)
                
                # Récupérer le status actuel
                operation = genai_client.operations.get(operation)
                
                op_obj = operation
                
            except Exception as get_err:
                print(f"   ❌ Erreur récupération opération: {get_err}")
                import traceback
                traceback.print_exc()
                
                # Si 404 ou similaire, marquer comme expirée
                if "404" in str(get_err) or "not found" in str(get_err).lower():
                    handle_veo_failure(video_id, op_data, "Opération expirée ou introuvable")
                continue
            
            # Vérifier si terminée
            done = op_obj.done if hasattr(op_obj, 'done') else False
            
            if done:
                # Vérifier si erreur
                if hasattr(op_obj, 'error') and op_obj.error:
                    error_msg = str(op_obj.error)
                    print(f"   ❌ Erreur: {error_msg}")
                    handle_veo_failure(video_id, op_data, error_msg)
                else:
                    print(f"   ✅ Terminé !")
                    # Récupérer le résultat
                    handle_veo_success(video_id, op_data, op_obj)
                
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


def handle_veo_success(video_id, op_data, op_obj):
    """Opération réussie → Télécharger et lancer bloc suivant ou assembler"""
    
    current_block = op_data['current_block']
    total_blocks = op_data['total_blocks']
    blocks = op_data['blocks']
    
    print(f"\n   📥 Traitement bloc {current_block}...")
    
    try:
        # Récupérer depuis response
        # Selon la documentation Veo 3.1: operation.response.generated_videos
        if not hasattr(op_obj, 'response') or not op_obj.response:
            print(f"   ❌ Pas de réponse dans l'opération")
            # Vérifier si erreur cachée
            if hasattr(op_obj, 'error') and op_obj.error:
                print(f"   ❌ Erreur détectée: {op_obj.error}")
                handle_veo_failure(video_id, op_data, str(op_obj.error))
            else:
                handle_veo_failure(video_id, op_data, "Aucune réponse dans l'opération")
            return
        
        response = op_obj.response
        
        # Les vidéos sont dans response.generated_videos (selon doc officielle)
        if not hasattr(response, 'generated_videos') or not response.generated_videos or len(response.generated_videos) == 0:
            print(f"   ❌ Aucune vidéo générée")
            print(f"   📊 Response debug: {dir(response)}")
            handle_veo_failure(video_id, op_data, "Aucune vidéo dans la réponse")
            return
        
        # L'URI de la vidéo - selon doc: generated_videos[0].video
        generated_video = response.generated_videos[0]
        
        # Le fichier vidéo est dans generated_video.video
        if not hasattr(generated_video, 'video') or not generated_video.video:
            print(f"   ❌ Pas de fichier vidéo")
            handle_veo_failure(video_id, op_data, "Pas de fichier vidéo dans la réponse")
            return
        
        video_file = generated_video.video
        
        print(f"   📍 Fichier vidéo détecté !")
        
        # STRATÉGIE : Ne télécharger QUE le dernier bloc (pour assemblage)
        # Les blocs intermédiaires sont conservés comme référence pour extensions
        # (accéder aux video_bytes "hydrate" l'objet → trop lourd pour l'API)
        
        if current_block == total_blocks:
            # Dernier bloc : télécharger et sauvegarder pour assemblage
            local_path = f'/tmp/{video_id}_block_{current_block}.mp4'
            
            if hasattr(video_file, 'video_bytes') and video_file.video_bytes:
                with open(local_path, 'wb') as f:
                    f.write(video_file.video_bytes)
                print(f"   ✅ Vidéo écrite depuis video_bytes: {len(video_file.video_bytes)} octets")
            elif hasattr(video_file, 'save'):
                video_file.save(local_path)
                print(f"   ✅ Vidéo sauvegardée via save()")
            else:
                video_bytes = bytes(video_file) if not isinstance(video_file, bytes) else video_file
                with open(local_path, 'wb') as f:
                    f.write(video_bytes)
                print(f"   ✅ Vidéo écrite via conversion: {len(video_bytes)} octets")
            
            # Upload vers Cloud Storage
            bucket = storage_client.bucket(BUCKET_NAME)
            video_blob = bucket.blob(f'{video_id}/block_{current_block}.mp4')
            video_blob.upload_from_filename(local_path)
            os.remove(local_path)
            
            print(f"   ✅ Bloc {current_block} sauvegardé: gs://{BUCKET_NAME}/{video_id}/block_{current_block}.mp4")
        else:
            # Bloc intermédiaire : NE PAS télécharger (gardé en référence pour extension)
            print(f"   ⏭️  Bloc {current_block} généré, référence conservée pour extension (non téléchargé)")
        
        # Si blocs restants → Lancer extension
        if current_block < total_blocks:
            next_block = current_block + 1
            # Passer generated_video.video AVANT tout accès aux bytes
            launch_extension(video_id, op_data, next_block, generated_video.video)
        else:
            # Tous blocs terminés → Déclencher assemblage
            print(f"\n   🎉 Tous les blocs terminés ({total_blocks}/{total_blocks})")
            trigger_assembly(video_id)
            
    except Exception as e:
        print(f"   ❌ Erreur traitement succès: {e}")
        import traceback
        traceback.print_exc()
        handle_veo_failure(video_id, op_data, str(e))


def launch_extension(video_id, op_data, next_block, previous_video_file):
    """Lance la génération du bloc suivant (extension)"""
    
    blocks = op_data['blocks']
    block_data = blocks[next_block - 1]  # Index 0-based
    
    print(f"\n   🔄 Lancement extension BLOC {next_block}...")
    print(f"      Dialogue: {block_data['dialogue'][:50]}...")
    print(f"      Durée: {block_data['duration']}s")
    
    try:
        # Construire prompt pour extension
        visual_prompt = block_data['visuel']
        dialogue = block_data['dialogue']
        full_prompt = f"{visual_prompt}\n\nDialogue: \"{dialogue}\""
        
        # Utiliser directement l'objet video_file du bloc précédent
        print(f"   📤 Utilisation de l'objet vidéo précédent...")
        
        # Lancer l'extension avec l'objet vidéo
        operation = genai_client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=full_prompt,
            video=previous_video_file,  # Objet vidéo du bloc précédent
            config=types.GenerateVideosConfig(
                duration_seconds=8,
                resolution="720p",
                aspect_ratio="9:16",
                person_generation="allow_all"
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
    """
    Prépare l'assemblage final.
    L'upload de block_N.mp4 déclenchera automatiquement agent-assembler-v2 (Cloud Storage trigger)
    """
    
    print(f"\n   🎬 Préparation assemblage...")
    
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
        
        print(f"   ✅ Firestore updated - block_N.mp4 déclenchera agent-assembler automatiquement")
        
    except Exception as e:
        print(f"   ❌ Erreur préparation assemblage: {e}")
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
            
            # Si bloc 1, génération initiale
            if current_block == 1:
                operation = genai_client.models.generate_videos(
                    model="veo-3.1-generate-preview",
                    prompt=full_prompt,
                    config=types.GenerateVideosConfig(
                        aspect_ratio="9:16",
                        resolution="720p",
                        duration_seconds=8,
                        person_generation="allow_all"
                    )
                )
            else:
                # Extension - utiliser vidéo précédente
                bucket = storage_client.bucket(BUCKET_NAME)
                prev_blob = bucket.blob(f'{video_id}/block_{current_block-1}.mp4')
                
                if prev_blob.exists():
                    prev_uri = f"gs://{BUCKET_NAME}/{video_id}/block_{current_block-1}.mp4"
                    
                    operation = genai_client.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        prompt=full_prompt,
                        video=prev_uri,
                        config=types.GenerateVideosConfig(
                            duration_seconds=8,
                            resolution="720p",
                            aspect_ratio="9:16",
                            person_generation="allow_all"
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
