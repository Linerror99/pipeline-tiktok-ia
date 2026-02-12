"""
Test du monitoring unifié V1 + V2
Simule la vérification des opérations Veo et le téléchargement des blocs

Usage:
  python test_monitor.py --video-id test_20260201_120000
"""

import os
import sys
import json
import argparse
from datetime import datetime
from google.cloud import storage, firestore

# Configuration
os.environ['GCP_PROJECT'] = 'reetik-project'
os.environ['BUCKET_NAME_V2'] = 'tiktok-pipeline-v2-artifacts-reetik-project'

PROJECT_ID = 'reetik-project'
LOCATION = 'us-central1'

def test_monitoring(video_id=None):
    """Test de monitoring des opérations Veo"""
    
    print("=" * 70)
    print(f"🔄 TEST MONITORING - check-and-retry-clips")
    print("=" * 70)
    
    # Clients
    firestore_client = firestore.Client()
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ['BUCKET_NAME_V2'])
    
    # ÉTAPE 1: Récupérer les opérations en cours
    print("\n📊 ÉTAPE 1: Récupération opérations en cours...")
    print("-" * 70)
    
    # Query Firestore pour V2
    v2_ops_ref = firestore_client.collection('v2_veo_operations')
    
    if video_id:
        query = v2_ops_ref.where('video_id', '==', video_id)
    else:
        query = v2_ops_ref.where('status', '==', 'generating_parallel')
    
    docs = list(query.stream())
    
    print(f"Opérations V2 trouvées: {len(docs)}")
    
    if len(docs) == 0:
        print("\n⚠️  Aucune opération en cours")
        print("\n💡 Lancez d'abord une génération:")
        print("   cd agent-video && python test_parallel.py")
        return
    
    # ÉTAPE 2: Vérifier chaque opération
    print("\n🔍 ÉTAPE 2: Vérification des opérations...")
    print("-" * 70)
    
    import vertexai
    from vertexai.preview.vision_models import VideoGenerationModel
    
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = VideoGenerationModel.from_pretrained("veo-3.1-fast")
    
    for doc in docs:
        data = doc.to_dict()
        vid_id = data['video_id']
        operations = data.get('operations', {})
        clips_status = data.get('clips_status', {})
        total_blocks = data['total_blocks']
        
        print(f"\n📹 Video ID: {vid_id}")
        print(f"   Total blocs: {total_blocks}")
        print(f"   Operations: {len(operations)}")
        
        # Vérifier chaque opération
        updated = False
        
        for block_num_str, op_name in operations.items():
            block_num = int(block_num_str)
            current_status = clips_status.get(block_num_str, 'unknown')
            
            print(f"\n   🎬 BLOC {block_num}:")
            print(f"      Status actuel: {current_status}")
            print(f"      Operation: {op_name[-30:]}")
            
            if current_status == 'completed':
                print(f"      ✅ Déjà complété, skip")
                continue
            
            try:
                # Récupérer l'opération
                from google.longrunning import operations_pb2
                from google.cloud import aiplatform_v1beta1
                
                ops_client = aiplatform_v1beta1.PredictionServiceClient()
                
                # Note: simplification - en prod utiliser l'API LRO
                print(f"      ⏳ Vérification opération...")
                
                # Simuler check (en réalité il faut utiliser operations_client.get_operation)
                # Pour ce test, on va juste afficher l'info
                print(f"      ℹ️  Pour vérifier l'opération:")
                print(f"         gcloud ai operations describe {op_name}")
                
                # Simuler téléchargement si done
                # En prod: if operation.done():
                simulate_done = False  # Changer en True pour tester download
                
                if simulate_done:
                    print(f"      ✅ Opération terminée!")
                    
                    # Simuler download
                    output_path = f"{vid_id}/block_{block_num}.mp4"
                    print(f"      📥 Download: gs://{bucket.name}/{output_path}")
                    
                    # Update status
                    clips_status[block_num_str] = 'completed'
                    updated = True
                else:
                    print(f"      ⏳ Encore en cours...")
                
            except Exception as e:
                print(f"      ❌ Erreur: {e}")
        
        # ÉTAPE 3: Update Firestore si changements
        if updated:
            print(f"\n   💾 Mise à jour Firestore...")
            
            # Vérifier si tous les blocs sont complétés
            completed_count = sum(1 for s in clips_status.values() if s == 'completed')
            
            if completed_count == total_blocks:
                print(f"   🎉 TOUS LES BLOCS COMPLÉTÉS!")
                data['status'] = 'ready_for_assembly'
                
                print(f"\n   🔔 Déclenchement assemblage...")
                print(f"      (En prod: appel HTTP à agent-assembler-v2)")
            else:
                print(f"   📊 Progression: {completed_count}/{total_blocks} blocs")
            
            data['clips_status'] = clips_status
            
            v2_ops_ref.document(vid_id).update(data)
            print(f"   ✅ Firestore mis à jour")
    
    # ÉTAPE 4: Résumé
    print("\n📊 RÉSUMÉ:")
    print("=" * 70)
    print(f"Vidéos surveillées: {len(docs)}")
    print("\n💡 Note:")
    print("   En production, cette fonction est appelée par Cloud Scheduler")
    print("   toutes les 1 minute pour vérifier l'avancement.")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-id', help="Video ID spécifique à surveiller")
    
    args = parser.parse_args()
    
    test_monitoring(args.video_id)
