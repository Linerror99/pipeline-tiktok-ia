"""
Script pour vérifier les fichiers uploadés dans Cloud Storage V2
"""
from google.cloud import storage

storage_client = storage.Client()
BUCKET_NAME = "tiktok-pipeline-v2-artifacts"

print("=" * 70)
print(f"🗂️  CONTENU DU BUCKET: {BUCKET_NAME}")
print("=" * 70)

bucket = storage_client.bucket(BUCKET_NAME)

# Lister tous les blobs
blobs = list(bucket.list_blobs())

if not blobs:
    print("\n⚠️ Le bucket est VIDE !\n")
else:
    print(f"\nNombre total de fichiers: {len(blobs)}\n")
    
    # Grouper par video_id
    videos = {}
    for blob in blobs:
        parts = blob.name.split('/')
        if len(parts) >= 2:
            video_id = parts[0]
            filename = '/'.join(parts[1:])
            
            if video_id not in videos:
                videos[video_id] = []
            videos[video_id].append(filename)
    
    # Afficher par vidéo
    for video_id in sorted(videos.keys()):
        print(f"📁 {video_id}/")
        for filename in sorted(videos[video_id]):
            # Afficher taille pour les MP4
            if filename.endswith('.mp4'):
                blob = bucket.blob(f"{video_id}/{filename}")
                size_mb = blob.size / (1024 * 1024) if blob.size else 0
                print(f"   ├─ {filename} ({size_mb:.2f} MB)")
            else:
                print(f"   ├─ {filename}")
        print()

print("=" * 70)
