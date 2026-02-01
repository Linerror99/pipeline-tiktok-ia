"""Vérifier les documents dans Firestore v2_veo_operations"""
from google.cloud import firestore

firestore_client = firestore.Client(project="reetik-project")

print("🔍 Vérification Firestore v2_veo_operations...")
print("=" * 70)

# Lister tous les documents
docs = firestore_client.collection('v2_veo_operations').limit(10).stream()

count = 0
for doc in docs:
    count += 1
    data = doc.to_dict()
    print(f"\n📄 Document: {doc.id}")
    print(f"   Status: {data.get('status')}")
    print(f"   Total blocks: {data.get('total_blocks')}")
    print(f"   Completed: {data.get('completed_blocks')}")
    print(f"   Operations: {len(data.get('operations', {}))}")
    print(f"   Created: {data.get('created_at')}")

if count == 0:
    print("\n⚠️  Aucun document trouvé dans v2_veo_operations")
    print("\nVérifions v2_video_status à la place:")
    print("=" * 70)
    
    status_docs = firestore_client.collection('v2_video_status').limit(10).stream()
    for doc in status_docs:
        data = doc.to_dict()
        print(f"\n📄 Document: {doc.id}")
        print(f"   Status: {data.get('status')}")
        print(f"   Created: {data.get('created_at')}")
else:
    print(f"\n✅ {count} document(s) trouvé(s)")
