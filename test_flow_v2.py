"""
Test complet du flow V2 end-to-end
Simule: Script → Video → Monitor → Assembler

Usage:
  python test_flow_v2.py --theme "Test IA" --duration 15
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime

# Configuration
os.environ['GCP_PROJECT'] = 'pipeline-video-ia'
os.environ['BUCKET_NAME'] = 'tiktok-pipeline-v2-artifacts'
os.environ['BUCKET_NAME_V2'] = 'tiktok-pipeline-v2-artifacts'

def test_flow_v2(theme, duration):
    """Test flow complet V2"""
    
    video_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=" * 70)
    print("🧪 TEST FLOW V2 COMPLET")
    print("=" * 70)
    print(f"Video ID: {video_id}")
    print(f"Thème: {theme}")
    print(f"Durée: {duration}s")
    print("=" * 70)
    
    # Import après config env
    from google.cloud import firestore
    
    firestore_client = firestore.Client()
    
    # ÉTAPE 1: Test agent-script
    print("\n📝 ÉTAPE 1: Génération script...")
    print("-" * 70)
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-script'))
    from main import generate_script, calculate_blocks_count, parse_blocks
    
    # Mock request
    class MockRequest:
        def __init__(self, data):
            self.data = data
        def get_json(self, silent=True):
            return self.data
    
    request = MockRequest({
        'theme': theme,
        'video_id': video_id,
        'target_duration': duration
    })
    
    try:
        result, status = generate_script(request)
        
        if status == 200:
            print(f"✅ Script généré: {result['blocks_generated']} blocs")
            
            # Vérifier Firestore
            status_doc = firestore_client.collection('v2_video_status').document(video_id).get()
            if status_doc.exists:
                print(f"✅ Firestore v2_video_status créé")
        else:
            print(f"❌ Erreur script: {result}")
            return
            
    except Exception as e:
        print(f"❌ Erreur étape 1: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ÉTAPE 2: Test agent-video (simulation)
    print("\n🎬 ÉTAPE 2: Génération vidéo (simulation)...")
    print("-" * 70)
    print("⚠️  Cette étape nécessite appel réel à Veo 3.1")
    print("    Pour tester localement:")
    print(f"    1. Créer bucket: gsutil mb gs://tiktok-pipeline-v2-artifacts")
    print(f"    2. Déployer agent-video sur Cloud Run")
    print(f"    3. Appeler: POST https://agent-video-v2.run.app")
    print(f"       Body: {{'video_id': '{video_id}'}}")
    
    # Simuler création operation Firestore
    blocks_count = calculate_blocks_count(duration)
    
    firestore_client.collection('v2_veo_operations').document(video_id).set({
        'video_id': video_id,
        'status': 'generating_block_1',
        'operation_name': 'projects/.../operations/simulated',
        'blocks': [],
        'current_block': 1,
        'total_blocks': blocks_count,
        'created_at': firestore.SERVER_TIMESTAMP,
        'veo_version': '3.1-fast',
        'retry_count': 0
    })
    
    print(f"✅ Simulation: v2_veo_operations créé ({blocks_count} blocs)")
    
    # ÉTAPE 3: Test monitor (simulation)
    print("\n🔍 ÉTAPE 3: Monitoring opérations (simulation)...")
    print("-" * 70)
    print("⚠️  Le monitor vérifie les opérations Veo toutes les minutes")
    print("    Pour tester:")
    print("    1. Déployer monitor-veo31 sur Cloud Run")
    print("    2. Créer Cloud Scheduler:")
    print("       gcloud scheduler jobs create http monitor-veo31")
    print("       --schedule='* * * * *'")
    print("       --uri=https://monitor-veo31.run.app")
    
    print(f"✅ Simulation: Monitor détecterait {blocks_count} opérations")
    
    # ÉTAPE 4: Test assembler (simulation)
    print("\n🎞️ ÉTAPE 4: Assemblage final (simulation)...")
    print("-" * 70)
    print("⚠️  L'assembleur nécessite:")
    print("    1. Vidéo finale dans gs://bucket/video_id/block_N.mp4")
    print("    2. FFmpeg installé")
    print("    3. Whisper installé")
    print("    Pour tester:")
    print("    1. Uploader une vidéo test dans le bucket")
    print("    2. Appeler agent-assembler localement ou déployé")
    
    print(f"✅ Simulation: Assembleur traiterait block_{blocks_count}.mp4")
    
    # RÉSUMÉ
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ TEST FLOW V2")
    print("=" * 70)
    print(f"✅ Script généré: {result['blocks_generated']} blocs")
    print(f"✅ Firestore initialisé: v2_video_status + v2_veo_operations")
    print(f"⚠️  Étapes restantes nécessitent déploiement Cloud")
    print("")
    print("Pour tester en VRAI:")
    print("1. Créer bucket V2:")
    print("   bash setup-v2-bucket.sh")
    print("")
    print("2. Déployer agents V2:")
    print("   bash build-and-push-v2.sh")
    print("   bash deploy-v2.sh")
    print("")
    print("3. Tester end-to-end via Backend API")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='Test flow V2 complet')
    parser.add_argument('--theme', type=str, default='Intelligence Artificielle',
                        help='Thème de la vidéo')
    parser.add_argument('--duration', type=int, default=15,
                        help='Durée cible (8, 15, 36, 60)')
    
    args = parser.parse_args()
    
    test_flow_v2(args.theme, args.duration)

if __name__ == "__main__":
    main()
