import functions_framework
from google.cloud import storage, firestore
import subprocess
import tempfile
from pathlib import Path
import whisper
import os
from datetime import datetime, timedelta

storage_client = storage.Client()
firestore_client = firestore.Client()

# Variable globale pour le modèle Whisper (chargé une seule fois)
WHISPER_MODEL = None

def get_whisper_model():
    """Charge le modèle Whisper (une seule fois, puis en cache)"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        print("📦 Chargement du modèle Whisper (base)...")
        WHISPER_MODEL = whisper.load_model("base")
        print("  ✓ Modèle chargé")
    return WHISPER_MODEL

def generate_whisper_subtitles(audio_path, output_ass_path):
    """
    Génère des sous-titres avec Whisper - Synchronisation PARFAITE
    """
    print("🎙️ Transcription avec Whisper (open-source)...")
    
    model = get_whisper_model()
    
    # Transcrire avec timestamps par mot
    result = model.transcribe(
        audio_path,
        language="fr",
        word_timestamps=True,  # CRUCIAL
        verbose=False
    )
    
    print(f"  ✓ Transcription terminée")
    
    # === En-tête ASS optimisé TikTok ===
    ass_header = """[Script Info]
Title: TikTok Whisper Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,10,10,80,1
Style: Highlight,Arial Black,95,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,7,3,2,10,10,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_events = []
    
    # Extraire tous les mots avec leurs timestamps
    all_words = []
    for segment in result["segments"]:
        if "words" in segment:
            for word_data in segment["words"]:
                all_words.append({
                    "word": word_data["word"].strip(),
                    "start": word_data["start"],
                    "end": word_data["end"]
                })
    
    print(f"  ✓ {len(all_words)} mots extraits")
    
    if not all_words:
        print("⚠️ Aucun mot détecté")
        return False
    
    # Grouper par 2 mots pour lisibilité
    segment_size = 2
    
    for i in range(0, len(all_words), segment_size):
        segment = all_words[i:i+segment_size]
        
        if not segment:
            continue
        
        start_time = segment[0]['start']
        end_time = segment[-1]['end']
        
        # Petite avance de 50ms pour anticipation
        start_time = max(0, start_time - 0.05)
        end_time = max(start_time + 0.1, end_time - 0.05)
        
        # Texte en MAJUSCULES
        text = " ".join([w['word'].upper() for w in segment])
        
        # Point de highlight (35% du temps)
        highlight_point = start_time + (end_time - start_time) * 0.35
        
        start_ass = format_timestamp_ass(start_time)
        highlight_ass = format_timestamp_ass(highlight_point)
        end_ass = format_timestamp_ass(end_time)
        
        # Blanc → Jaune
        ass_events.append(f"Dialogue: 0,{start_ass},{highlight_ass},Default,,0,0,0,,{text}")
        ass_events.append(f"Dialogue: 0,{highlight_ass},{end_ass},Highlight,,0,0,0,,{text}")
    
    # Écrire le fichier ASS
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_header)
        f.write("\n".join(ass_events))
    
    print(f"  ✓ {len(ass_events)} événements ASS générés avec Whisper")
    return True

def format_timestamp_ass(seconds):
    """Convertit des secondes en format ASS (H:MM:SS.cc)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

@functions_framework.http
def assemble_video(request):
    """
    Agent Assembleur avec Whisper - Déclenché par HTTP
    Reçoit: {"video_id": "theme_123456"}
    """
    # Récupérer le video_id depuis la requête
    request_json = request.get_json(silent=True)
    
    if not request_json or 'video_id' not in request_json:
        return {"error": "Missing video_id in request body"}, 400
    
    video_base_name = request_json['video_id']
    
    print(f"🎬 Assemblage déclenché pour : {video_base_name}")
    
    # Récupérer les infos depuis Firestore
    video_status_doc = firestore_client.collection('video_status').document(video_base_name).get()
    
    if not video_status_doc.exists:
        print(f"❌ Document video_status non trouvé pour {video_base_name}")
        return {"error": "Video status not found"}, 404
    
    video_status = video_status_doc.to_dict()
    bucket_name = video_status.get('bucket_name', f'tiktok-pipeline-artifacts-{os.environ.get("GCP_PROJECT")}')
    clips = video_status['clips']
    
    print(f"📊 Status vidéo: {video_status['status']}")
    print(f"📊 Clips attendus: {video_status['total_clips']}")
    print(f"� Clips complétés: {video_status['completed_clips']}")

    bucket = storage_client.bucket(bucket_name)
    prefix = f"video_clips/{video_base_name}/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    video_clips = sorted([b.name for b in blobs if b.name.endswith(".mp4")])
    print(f"📊 Clips trouvés dans GCS : {len(video_clips)}")

    # Lire le script
    script_file_name = f"script_{video_base_name}.txt"
    try:
        script_blob = bucket.blob(script_file_name)
        if not script_blob.exists():
            print(f"❌ Script non trouvé")
            return {"error": "Script not found"}, 404
        script_content = script_blob.download_as_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Erreur script : {e}")
        return {"error": f"Script error: {str(e)}"}, 500

    expected_clips = script_content.upper().count("VISUEL")
    print(f"🎯 Clips attendus (depuis script) : {expected_clips}")

    # Vérifier si déjà assemblé
    final_video_name = f"final_{video_base_name}.mp4"
    final_blob = bucket.blob(final_video_name)
    if final_blob.exists():
        print(f"✅ Vidéo finale existe déjà")
        return {"status": "already_exists", "video_id": video_base_name}, 200

    print("🎉 Lancement de l'assemblage avec Whisper...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        print("📥 Téléchargement des clips...")
        clip_files = []
        for i, clip_name in enumerate(video_clips):
            local_clip_path = tmpdir_path / f"clip_{i:03d}.mp4"
            bucket.blob(clip_name).download_to_filename(str(local_clip_path))
            clip_files.append(local_clip_path)
            print(f"  ✓ Clip {i+1}/{len(video_clips)}")

        # Télécharger l'audio
        audio_file_name = f"audio_{video_base_name}.mp3"
        audio_blob = bucket.blob(audio_file_name)
        if not audio_blob.exists():
            print(f"❌ Audio non trouvé")
            return "Error"
        
        local_audio_path = tmpdir_path / "narration.mp3"
        audio_blob.download_to_filename(str(local_audio_path))
        print(f"🎵 Audio téléchargé")

        # Générer les sous-titres avec Whisper
        ass_path = tmpdir_path / "subtitles.ass"
        subtitles_generated = generate_whisper_subtitles(str(local_audio_path), str(ass_path))

        # Fichier de concaténation
        concat_file = tmpdir_path / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for clip_file in clip_files:
                f.write(f"file '{clip_file.absolute()}'\n")

        print("🎬 Étape 1/3 : Concaténation...")
        concat_video = tmpdir_path / "concat_video.mp4"
        try:
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(concat_file),
                '-c', 'copy', '-y', str(concat_video)
            ], capture_output=True, check=True, text=True)
            print("  ✓ Concaténé")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur concat : {e.stderr}")
            return "Error"

        print("🎬 Étape 2/3 : Audio...")
        video_with_audio = tmpdir_path / "video_with_audio.mp4"
        try:
            subprocess.run([
                'ffmpeg', '-i', str(concat_video), '-i', str(local_audio_path),
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-y', str(video_with_audio)
            ], capture_output=True, check=True, text=True)
            print("  ✓ Audio")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur audio : {e.stderr}")
            return "Error"

        # Sous-titres
        if subtitles_generated and ass_path.exists():
            print("🎬 Étape 3/3 : Sous-titres Whisper...")
            final_video = tmpdir_path / "final_video.mp4"
            try:
                subprocess.run([
                    'ffmpeg', '-i', str(video_with_audio),
                    '-vf', f"ass={str(ass_path)}",
                    '-c:a', 'copy',
                    '-y', str(final_video)
                ], capture_output=True, check=True, text=True)
                print("  ✓ Sous-titres Whisper")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Erreur sous-titres : {e.stderr[-500:]}")
                final_video = video_with_audio
        else:
            print("⚠️ Pas de sous-titres")
            final_video = video_with_audio

        if not final_video.exists() or final_video.stat().st_size == 0:
            print("❌ Vidéo vide")
            return "Error"

        final_size_mb = final_video.stat().st_size / (1024 * 1024)
        print(f"📤 Upload ({final_size_mb:.2f} MB)...")

        try:
            final_blob.upload_from_filename(str(final_video), content_type="video/mp4")
            final_video_url = f"gs://{bucket_name}/{final_video_name}"
            print(f"✅ SUCCÈS ! {final_video_url}")
            
            # Mettre à jour Firestore : status = completed
            firestore_client.collection('video_status').document(video_base_name).update({
                'status': 'completed',
                'final_video_url': final_video_url,
                'updated_at': datetime.utcnow()
            })
            print(f"📝 Firestore mis à jour : status=completed")
            
        except Exception as e:
            print(f"❌ Erreur upload : {e}")
            
            # Mettre à jour Firestore : status = failed
            firestore_client.collection('video_status').document(video_base_name).update({
                'status': 'failed',
                'error': str(e),
                'updated_at': datetime.utcnow()
            })
            
            return {"error": f"Upload error: {str(e)}"}, 500

    print(f"🎉 ASSEMBLAGE WHISPER TERMINÉ !")
    
    return {
        "status": "success",
        "video_id": video_base_name,
        "final_video_url": f"gs://{bucket_name}/{final_video_name}"
    }, 200