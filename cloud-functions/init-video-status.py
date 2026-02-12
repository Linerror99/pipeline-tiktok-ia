#!/usr/bin/env python3
"""
Script pour initialiser/réinitialiser les documents video_status
pour toutes les vidéos existantes dans GCS
"""
from google.cloud import storage, firestore
import re

PROJECT_ID = "reetik-project"
BUCKET_NAME = "tiktok-pipeline-artifacts-reetik-project"

storage_client = storage.Client(project=PROJECT_ID)
firestore_client = firestore.Client(project=PROJECT_ID)

def find_all_videos():
    """
    Trouve toutes les vidéos qui ont des clips dans GCS
    """
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Lister tous les préfixes dans video_clips/
    blobs = bucket.list_blobs(prefix="video_clips/", delimiter="/")
    
    # Les préfixes sont les noms de vidéos
    video_ids = set()
    for page in blobs.pages:
        for prefix in page.prefixes:
            # prefix format: "video_clips/theme_123456/"
            match = re.search(r'video_clips/([^/]+)/', prefix)
            if match:
                video_ids.add(match.group(1))
    
    return sorted(video_ids)

def count_clips_in_gcs(bucket, video_id):
    """
    Compte combien de clips .mp4 existent dans GCS pour cette vidéo
    """
    prefix = f"video_clips/{video_id}/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    clips = {}
    for blob in blobs:
        if blob.name.endswith('.mp4'):
            # Extraire le numéro de clip
            match = re.search(rf'video_clips/{re.escape(video_id)}/clip_(\d+)/', blob.name)
            if match:
                clip_num = match.group(1)
                clips[clip_num] = f"gs://{BUCKET_NAME}/{blob.name}"
    
    return clips

def check_if_final_exists(bucket, video_id):
    """
    Vérifie si la vidéo finale existe
    """
    final_blob = bucket.blob(f"final_{video_id}.mp4")
    return final_blob.exists()

def init_or_update_video_status(video_id):
    """
    Crée ou met à jour le document video_status pour une vidéo
    """
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Vérifier si la vidéo finale existe
    final_exists = check_if_final_exists(bucket, video_id)
    
    if final_exists:
        print(f"  ✅ {video_id} : Vidéo finale existe déjà, skip")
        return "completed"
    
    # Compter les clips dans GCS
    clips_in_gcs = count_clips_in_gcs(bucket, video_id)
    
    if not clips_in_gcs:
        print(f"  ⚠️  {video_id} : Aucun clip trouvé")
        return "no_clips"
    
    print(f"  📊 {video_id} : {len(clips_in_gcs)} clips trouvés dans GCS")
    
    # Vérifier si le document existe déjà
    doc_ref = firestore_client.collection('video_status').document(video_id)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        current_status = data.get('status')
        
        if current_status == 'completed':
            print(f"     → Status déjà 'completed', skip")
            return "already_completed"
        
        print(f"     → Document existe (status: {current_status}), mise à jour...")
        
        # Mettre à jour les clips avec les URIs GCS
        clips_data = data.get('clips', {})
        for clip_num, gcs_uri in clips_in_gcs.items():
            if clip_num in clips_data:
                clips_data[clip_num]['status'] = 'ready'
                clips_data[clip_num]['gcs_uri'] = gcs_uri
            else:
                # Clip pas dans Firestore, le créer
                clips_data[clip_num] = {
                    'status': 'ready',
                    'gcs_uri': gcs_uri,
                    'operation_name': None,
                    'prompt': '',
                    'retry_count': 0
                }
        
        # Mettre à jour le document
        doc_ref.update({
            'clips': clips_data,
            'completed_clips': len(clips_in_gcs),
            'total_clips': max(len(clips_in_gcs), data.get('total_clips', len(clips_in_gcs))),
            'status': 'processing'  # Remettre en processing pour que le monitor le traite
        })
        
        print(f"     ✅ Mis à jour : {len(clips_in_gcs)} clips ready, status=processing")
        return "updated"
    
    else:
        print(f"     → Document n'existe pas, création...")
        
        # Créer le document
        clips_data = {}
        for clip_num, gcs_uri in clips_in_gcs.items():
            clips_data[clip_num] = {
                'status': 'ready',
                'gcs_uri': gcs_uri,
                'operation_name': None,
                'prompt': '',
                'retry_count': 0
            }
        
        from datetime import datetime
        doc_ref.set({
            'video_id': video_id,
            'status': 'processing',
            'total_clips': len(clips_in_gcs),
            'completed_clips': len(clips_in_gcs),
            'bucket_name': BUCKET_NAME,
            'clips': clips_data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        print(f"     ✅ Créé : {len(clips_in_gcs)} clips ready, status=processing")
        return "created"

def main():
    print("🔍 Recherche de toutes les vidéos dans GCS...")
    print(f"   Bucket: {BUCKET_NAME}\n")
    
    video_ids = find_all_videos()
    
    print(f"📹 {len(video_ids)} vidéo(s) trouvée(s) :\n")
    
    stats = {
        'completed': 0,
        'updated': 0,
        'created': 0,
        'no_clips': 0,
        'already_completed': 0
    }
    
    for video_id in video_ids:
        result = init_or_update_video_status(video_id)
        stats[result] += 1
        print()
    
    print("=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    print(f"  ✅ Vidéos complètes (avec final) : {stats['completed']}")
    print(f"  ✅ Vidéos déjà marquées completed : {stats['already_completed']}")
    print(f"  🔄 Documents mis à jour : {stats['updated']}")
    print(f"  ✨ Documents créés : {stats['created']}")
    print(f"  ⚠️  Vidéos sans clips : {stats['no_clips']}")
    print()
    print(f"🎯 {stats['updated'] + stats['created']} vidéo(s) prête(s) pour le monitor")
    print()
    print("💡 Prochaine étape : Lancer le monitor manuellement")
    print("   curl -X POST https://monitor-and-assemble-5ranhgrf2q-uc.a.run.app \\")
    print("     -H 'Content-Type: application/json' -d '{}'")

if __name__ == '__main__':
    main()
