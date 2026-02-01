import functions_framework
from google.cloud import storage, firestore
import subprocess
import tempfile
from pathlib import Path
import whisper
import os
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()

# Configuration V2
BUCKET_NAME_V2 = os.environ.get("BUCKET_NAME_V2", "tiktok-pipeline-v2-artifacts")

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

def generate_whisper_subtitles_from_video(video_path, output_ass_path):
    """
    Génère des sous-titres Whisper DIRECTEMENT depuis la vidéo
    (pas besoin d'extraction audio séparée)
    """
    print("🎙️ Transcription Whisper depuis vidéo...")
    
    try:
        model = get_whisper_model()
        
        # Whisper peut transcrir directement depuis vidéo !
        result = model.transcribe(
            video_path,  # Accepte vidéo OU audio
            language="fr",
            word_timestamps=True,
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

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        ass_events = []
        
        # Extraire tous les mots
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
        
        # Grouper par 2 mots
        segment_size = 2
        
        for i in range(0, len(all_words), segment_size):
            segment = all_words[i:i+segment_size]
            
            if not segment:
                continue
            
            start_time = max(0, segment[0]['start'] - 0.05)
            end_time = max(start_time + 0.1, segment[-1]['end'] - 0.05)
            
            text = " ".join([w['word'].upper() for w in segment])
            
            start_ass = format_ass_time(start_time)
            end_ass = format_ass_time(end_time)
            
            ass_events.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}")
        
        # Écrire fichier ASS
        with open(output_ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            f.write("\n".join(ass_events))
        
        print(f"  ✓ Fichier ASS créé: {len(ass_events)} sous-titres")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur Whisper: {e}")
        import traceback
        traceback.print_exc()
        return False


def format_ass_time(seconds):
    """Convertit secondes en format ASS (0:00:00.00)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_whisper_subtitles_from_video(video_path, output_ass_path):
    """
    Génère des sous-titres Whisper DIRECTEMENT depuis la vidéo
    (pas besoin d'extraction audio séparée)
    """
    print("🎙️ Transcription Whisper depuis vidéo...")
    
    try:
        model = get_whisper_model()
        
        # Whisper peut transcrire directement depuis vidéo !
        result = model.transcribe(
            video_path,  # Accepte vidéo OU audio
            language="fr",
            word_timestamps=True,
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
        
        # Extraire tous les mots
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
        
    except Exception as e:
        print(f"  ❌ Erreur Whisper: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_whisper_subtitles(audio_path, output_ass_path):
    """
    DEPRECATED - Utiliser generate_whisper_subtitles_from_video à la place
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

@functions_framework.cloud_event
def assemble_video(cloudevent):
    """
    Cloud Function déclenchée par upload de block_N.mp4 (dernier bloc)
    Ajoute sous-titres Whisper sur vidéo finale
    
    CloudEvent data:
    {
        "bucket": "tiktok-pipeline-v2-artifacts",
        "name": "{video_id}/block_N.mp4"
    }
    """
    try:
        data = cloudevent.data
        bucket_name = data["bucket"]
        file_name = data["name"]
        
        print(f"📡 Déclencheur reçu pour le fichier : {file_name}")
        
        # Vérifier que c'est bien un block_*.mp4 ET que c'est un déclenchement pour assembly
        # (monitor-veo31 upload block_N.mp4 avec metadata assembly=true)
        if not "/block_" in file_name or not file_name.endswith(".mp4"):
            print(f"⚠️ Fichier non-block {file_name}. Traitement ignoré.")
            return "OK"
        
        # Extraire video_id du path: {video_id}/block_N.mp4
        video_id = file_name.split("/")[0]
        
        print(f"🎞️ Assemblage final pour video_id: {video_id}")
        
    except Exception as e:
        print(f"❌ Erreur parsing CloudEvent: {e}")
        return "ERROR"
    
    print("=" * 70)
    print(f"🎬 Assemblage V2 pour: {video_id}")
    print("=" * 70)
    
    try:
        # Récupérer infos depuis Firestore
        op_doc = firestore_client.collection('v2_veo_operations').document(video_id).get()
        
        if not op_doc.exists:
            print(f"❌ v2_veo_operations/{video_id} non trouvé")
            return "ERROR"
        
        op_data = op_doc.to_dict()
        total_blocks = op_data['total_blocks']
        
        print(f"📊 Total blocs: {total_blocks}")
        
        # Récupérer LA vidéo finale (block_N.mp4 contient TOUS les blocs assemblés)
        bucket = storage_client.bucket(BUCKET_NAME_V2)
        final_block_blob = bucket.blob(f'{video_id}/block_{total_blocks}.mp4')
        
        if not final_block_blob.exists():
            return {"error": f"Vidéo finale block_{total_blocks}.mp4 non trouvée"}, 404
        
        print(f"✅ Vidéo finale trouvée: block_{total_blocks}.mp4")
        
        # Créer répertoire temp
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Télécharger vidéo finale
            final_video = tmpdir_path / "final_video.mp4"
            final_block_blob.download_to_filename(str(final_video))
            print(f"📥 Vidéo téléchargée: {final_video}")
            
            # 1. Extraire audio de la vidéo
            audio_path = tmpdir_path / "audio.wav"
            print("\n🎵 Extraction audio...")
            subprocess.run([
                'ffmpeg', '-i', str(final_video),
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1',
                str(audio_path)
            ], check=True, capture_output=True)
            print("  ✓ Audio extrait")
            
            # 2. Whisper sur audio
            print("\n🎙️ Transcription Whisper...")
            ass_path = tmpdir_path / "subtitles.ass"
            success = generate_whisper_subtitles(str(audio_path), str(ass_path))
            
            if not success:
                return {"error": "Échec génération sous-titres Whisper"}, 500
            
            # 3. Ajouter sous-titres à la vidéo
            final_with_subs = tmpdir_path / "final_with_subs.mp4"
            print("\n📝 Ajout sous-titres...")
            subprocess.run([
                'ffmpeg', '-i', str(final_video),
                '-vf', f"ass={ass_path}",
                '-c:a', 'copy',
                str(final_with_subs)
            ], check=True, capture_output=True)
            print("  ✓ Sous-titres ajoutés")
            
            # 4. Upload vidéo finale
            final_blob = bucket.blob(f'{video_id}/final.mp4')
            final_blob.upload_from_filename(str(final_output))
            public_url = f"gs://{BUCKET_NAME_V2}/{video_id}/final.mp4"
            
            print(f"\n✅ Vidéo finale uploadée: {public_url}")
            
            # 5. Update Firestore
            firestore_client.collection('v2_veo_operations').document(video_id).update({
                'status': 'completed',
                'final_url': public_url,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            firestore_client.collection('v2_video_status').document(video_id).update({
                'status': 'completed',
                'final_url': public_url,
                'completed_at': firestore.SERVER_TIMESTAMP
            })
            
            print("\n" + "=" * 70)
            print(f"🎉 Assemblage V2 terminé !")
            print("=" * 70)
            
            return {
                "status": "success",
                "video_id": video_id,
                "final_url": public_url,
                "total_blocks": total_blocks
            }, 200
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Erreur FFmpeg: {e.stderr.decode() if e.stderr else str(e)}"
        print(f"❌ {error_msg}")
        mark_as_failed(video_id, error_msg)
        return {"error": error_msg}, 500
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur: {error_msg}")
        import traceback
        traceback.print_exc()
        mark_as_failed(video_id, error_msg)
        return {"error": error_msg}, 500


def mark_as_failed(video_id, error_message):
    """Marque la vidéo comme échouée"""
    try:
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': 'failed',
            'error_message': error_message,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        firestore_client.collection('v2_video_status').document(video_id).update({
            'status': 'error',
            'error_message': f'Assemblage échoué: {error_message}',
            'updated_at': firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print(f"⚠️ Erreur update Firestore: {e}")
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