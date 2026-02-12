"""
Test de génération parallèle avec Veo 3.1 Fast
Simule le lancement de N générations vidéo simultanées

Usage:
  python test_parallel.py --video-id test_20260201_120000
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

def test_parallel_generation(video_id):
    """Test de génération parallèle"""
    
    print("=" * 70)
    print(f"🧪 TEST GÉNÉRATION PARALLÈLE - Veo 3.1 Fast")
    print("=" * 70)
    print(f"Video ID: {video_id}")
    print("=" * 70)
    
    # Clients
    storage_client = storage.Client()
    firestore_client = firestore.Client()
    bucket = storage_client.bucket(os.environ['BUCKET_NAME_V2'])
    
    # ÉTAPE 1: Vérifier que script_v2.json existe
    print("\n📝 ÉTAPE 1: Vérification script...")
    print("-" * 70)
    
    script_path = f"{video_id}/script_v2.json"
    blob = bucket.blob(script_path)
    
    if not blob.exists():
        print(f"❌ Script introuvable: gs://{bucket.name}/{script_path}")
        print("\n💡 Créez d'abord un script:")
        print(f"   cd agent-script && python test_simple.py")
        return
    
    # Télécharger et parser script
    script_data = json.loads(blob.download_as_text())
    blocks = script_data.get('blocks', [])
    total_blocks = len(blocks)
    
    print(f"✅ Script trouvé: {total_blocks} blocs")
    
    # ÉTAPE 2: Simuler génération parallèle
    print("\n🎬 ÉTAPE 2: Lancement générations parallèles...")
    print("-" * 70)
    
    import vertexai
    from vertexai.preview.vision_models import VideoGenerationModel
    
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = VideoGenerationModel.from_pretrained("veo-3.1-fast")
    
    operations = {}
    clips_status = {}
    
    for i, block in enumerate(blocks, 1):
        dialogue = block.get('dialogue', '')
        visuel = block.get('visuel', '')
        duration = block.get('duration', 7)
        
        # Construire prompt
        prompt = f"{dialogue}. {visuel}"
        
        print(f"\n  🎥 BLOC {i}/{total_blocks} ({duration}s)")
        print(f"     Prompt: {prompt[:60]}...")
        
        try:
            # Lancer génération asynchrone
            print(f"     ⏳ Appel Veo 3.1 Fast...")
            
            response = model.generate_videos(
                prompt=prompt,
                number_of_videos=1,
                aspect_ratio="9:16",
                video_length=f"{duration}s"
            )
            
            operation_name = response.operation.name
            operations[i] = operation_name
            clips_status[i] = "generating"
            
            print(f"     ✅ Operation lancée: {operation_name[-30:]}")
            
        except Exception as e:
            print(f"     ❌ Erreur: {e}")
            clips_status[i] = "failed"
    
    # ÉTAPE 3: Sauvegarder dans Firestore
    print("\n💾 ÉTAPE 3: Sauvegarde Firestore...")
    print("-" * 70)
    
    doc_data = {
        'video_id': video_id,
        'status': 'generating_parallel',
        'operations': operations,
        'clips_status': clips_status,
        'total_blocks': total_blocks,
        'current_block': None,  # Plus utilisé en V2
        'created_at': firestore.SERVER_TIMESTAMP,
        'veo_version': '3.1-fast',
        'retry_count': 0
    }
    
    firestore_client.collection('v2_veo_operations').document(video_id).set(doc_data)
    
    print(f"✅ Document créé: v2_veo_operations/{video_id}")
    print(f"   - Status: generating_parallel")
    print(f"   - Operations: {len(operations)} lancées")
    print(f"   - Clips status: {clips_status}")
    
    # ÉTAPE 4: Résumé
    print("\n📊 RÉSUMÉ:")
    print("=" * 70)
    print(f"Total blocs: {total_blocks}")
    print(f"Générations lancées: {len(operations)}")
    print(f"Générations échouées: {sum(1 for s in clips_status.values() if s == 'failed')}")
    print("\n⏱️  Temps estimé: ~8-12 minutes")
    print("\n🔄 Prochaine étape:")
    print("   Le scheduler 'check-and-retry-clips' va surveiller ces opérations")
    print("   et télécharger les blocs dès qu'ils sont prêts.")
    print("=" * 70)

def create_mock_script(video_id, theme="Test IA", blocks_count=3):
    """Créer un script de test si besoin"""
    
    print(f"\n📝 Création script de test: {blocks_count} blocs...")
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(os.environ['BUCKET_NAME_V2'])
    
    blocks = []
    for i in range(1, blocks_count + 1):
        duration = 8 if i == 1 else 7
        blocks.append({
            'block_number': i,
            'duration': duration,
            'dialogue': f"Dialogue du bloc {i} sur {theme}",
            'visuel': f"Scène visuelle pour le bloc {i}"
        })
    
    script_data = {
        'video_id': video_id,
        'theme': theme,
        'blocks': blocks,
        'total_blocks': blocks_count,
        'total_duration': 8 + (blocks_count - 1) * 7
    }
    
    script_path = f"{video_id}/script_v2.json"
    blob = bucket.blob(script_path)
    blob.upload_from_string(json.dumps(script_data, indent=2))
    
    print(f"✅ Script créé: gs://{bucket.name}/{script_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-id', default=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument('--create-script', action='store_true', help="Créer un script de test")
    parser.add_argument('--blocks', type=int, default=3, help="Nombre de blocs (si --create-script)")
    
    args = parser.parse_args()
    
    if args.create_script:
        create_mock_script(args.video_id, blocks_count=args.blocks)
    
    test_parallel_generation(args.video_id)
