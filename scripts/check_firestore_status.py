"""
Script pour vérifier l'état des opérations V2 dans Firestore
"""
from google.cloud import firestore
from datetime import datetime

firestore_client = firestore.Client()

print("=" * 70)
print("🔍 ÉTAT DES OPÉRATIONS VEO 3.1 DANS FIRESTORE")
print("=" * 70)

# Vérifier v2_veo_operations
print("\n📊 Collection: v2_veo_operations")
print("-" * 70)

ops = firestore_client.collection('v2_veo_operations').stream()
ops_list = list(ops)

print(f"Nombre total d'opérations: {len(ops_list)}\n")

for op_doc in ops_list:
    op_data = op_doc.to_dict()
    video_id = op_doc.id
    
    print(f"🎬 {video_id}")
    print(f"   Status: {op_data.get('status', 'N/A')}")
    print(f"   Bloc: {op_data.get('current_block', 'N/A')}/{op_data.get('total_blocks', 'N/A')}")
    print(f"   Operation: {op_data.get('operation_name', 'N/A')[:80]}...")
    
    if 'created_at' in op_data:
        created = op_data['created_at']
        if hasattr(created, 'timestamp'):
            age_seconds = (datetime.now().timestamp() - created.timestamp())
            age_minutes = int(age_seconds / 60)
            print(f"   Âge: {age_minutes} minutes")
    
    if 'error_message' in op_data:
        print(f"   ❌ Erreur: {op_data['error_message']}")
    
    print()

# Vérifier v2_video_status
print("\n📊 Collection: v2_video_status")
print("-" * 70)

videos = firestore_client.collection('v2_video_status').stream()
videos_list = list(videos)

print(f"Nombre total de vidéos: {len(videos_list)}\n")

for vid_doc in videos_list:
    vid_data = vid_doc.to_dict()
    video_id = vid_doc.id
    
    print(f"🎥 {video_id}")
    print(f"   Status: {vid_data.get('status', 'N/A')}")
    print(f"   Step: {vid_data.get('current_step', 'N/A')}")
    
    if 'error_message' in vid_data:
        print(f"   ❌ Erreur: {vid_data['error_message']}")
    
    print()

print("=" * 70)
