import functions_framework
from google.cloud import storage
from google.cloud import speech
import os
import subprocess
import tempfile
from pathlib import Path

storage_client = storage.Client()
speech_client = speech.SpeechClient()

def generate_ass_subtitles(audio_path, output_ass_path):
    """
    Génère un fichier ASS avec sous-titres style TikTok - version optimisée pour la synchro
    """
    print("🎙️ Transcription de l'audio avec timestamps par mot...")
    
    with open(audio_path, 'rb') as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        language_code="fr-FR",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
        model="latest_long",
    )

    try:
        response = speech_client.recognize(config=config, audio=audio)
    except Exception as e:
        print(f"❌ Erreur Speech-to-Text : {e}")
        return False

    # === En-tête du fichier ASS ===
    ass_header = """[Script Info]
Title: TikTok Style Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: White,Arial,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,10,10,120,1
Style: Yellow,Arial,80,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,10,10,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_events = []
    
    # Fonction helper pour convertir n'importe quel type de timestamp en secondes
    def to_seconds(time_obj):
        if hasattr(time_obj, 'seconds') and hasattr(time_obj, 'nanos'):
            return time_obj.seconds + (time_obj.nanos / 1_000_000_000.0)
        elif hasattr(time_obj, 'total_seconds'):
            return time_obj.total_seconds()
        else:
            return float(time_obj)
    
    # Collecter tous les mots avec leurs timestamps
    all_words = []
    for result in response.results:
        for word_info in result.alternatives[0].words:
            start_sec = to_seconds(word_info.start_time)
            end_sec = to_seconds(word_info.end_time)
            
            all_words.append({
                'word': word_info.word,
                'start': start_sec,
                'end': end_sec
            })
    
    print(f"  ✓ {len(all_words)} mots transcrits")
    
    # STRATÉGIE : Afficher 1-2 mots max par segment
    segment_size = 2
    
    for i in range(0, len(all_words), segment_size):
        segment = all_words[i:i+segment_size]
        
        if not segment:
            continue
        
        # Compensation de délai (AJUSTABLE)
        delay_offset = -0.05  # Avancer de 50ms
        
        start_time = max(0, segment[0]['start'] + delay_offset)
        end_time = segment[-1]['end'] + delay_offset
        
        # Texte du segment
        text = " ".join([word['word'] for word in segment])
        
        # Formater les timestamps ASS
        start_ass = format_timestamp_ass(start_time)
        end_ass = format_timestamp_ass(end_time)
        
        # Point milieu pour changement de couleur
        mid_time = (start_time + end_time) / 2
        mid_ass = format_timestamp_ass(mid_time)
        
        # Blanc → Jaune
        ass_events.append(f"Dialogue: 0,{start_ass},{mid_ass},White,,0,0,0,,{text}")
        ass_events.append(f"Dialogue: 0,{mid_ass},{end_ass},Yellow,,0,0,0,,{text}")
    
    # Écrire le fichier ASS
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_header)
        f.write("\n".join(ass_events))
    
    print(f"  ✓ {len(ass_events)} événements ASS générés")
    print(f"  ℹ️ Compensation : {delay_offset*1000:.0f}ms")
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
    Agent Assembleur avec Sous-titres Style TikTok (Synchro Optimisée)
    """
    data = cloudevent.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    print(f"🎬 Déclencheur reçu pour : {file_name}")

    if not file_name.startswith("video_clips/") or not file_name.endswith(".mp4"):
        print(f"❌ Fichier ignoré : {file_name}")
        return "OK"

    parts = file_name.split("/")
    if len(parts) < 3:
        print("❌ Structure invalide")
        return "OK"
    
    video_base_name = parts[1]
    print(f"📹 Clip détecté : {video_base_name}")

    bucket = storage_client.bucket(bucket_name)
    prefix = f"video_clips/{video_base_name}/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    video_clips = sorted([b.name for b in blobs if b.name.endswith(".mp4")])
    print(f"📊 Clips trouvés : {len(video_clips)}")

    script_file_name = f"script_{video_base_name}.txt"
    try:
        script_blob = bucket.blob(script_file_name)
        if not script_blob.exists():
            print(f"❌ Script non trouvé")
            return "OK"
        script_content = script_blob.download_as_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Erreur script : {e}")
        return "OK"

    expected_clips = script_content.upper().count("VISUEL")
    print(f"🎯 Clips attendus : {expected_clips}")

    if len(video_clips) < expected_clips:
        print(f"⏳ Attente de {expected_clips - len(video_clips)} clips")
        return "OK"

    final_video_name = f"final_{video_base_name}.mp4"
    final_blob = bucket.blob(final_video_name)
    if final_blob.exists():
        print(f"✅ Vidéo finale existe déjà")
        return "OK"

    print("🎉 Assemblage en cours...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        print("📥 Téléchargement...")
        
        clip_files = []
        for i, clip_name in enumerate(video_clips):
            local_clip_path = tmpdir_path / f"clip_{i:03d}.mp4"
            bucket.blob(clip_name).download_to_filename(str(local_clip_path))
            clip_files.append(local_clip_path)
            print(f"  ✓ Clip {i+1}/{len(video_clips)}")

        audio_file_name = f"audio_{video_base_name}.mp3"
        audio_blob = bucket.blob(audio_file_name)
        if not audio_blob.exists():
            print(f"❌ Audio non trouvé")
            return "Error"
        
        local_audio_path = tmpdir_path / "narration.mp3"
        audio_blob.download_to_filename(str(local_audio_path))
        print(f"🎵 Audio téléchargé")

        ass_path = tmpdir_path / "subtitles.ass"
        subtitles_generated = generate_ass_subtitles(str(local_audio_path), str(ass_path))

        concat_file = tmpdir_path / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for clip_file in clip_files:
                f.write(f"file '{clip_file.absolute()}'\n")

        print("🎬 Étape 1/3 : Concaténation...")
        concat_video = tmpdir_path / "concat_video.mp4"
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(concat_file),
            '-c', 'copy', '-y', str(concat_video)
        ], capture_output=True, check=True)
        print("  ✓ Concaténé")

        print("🎬 Étape 2/3 : Audio...")
        video_with_audio = tmpdir_path / "video_with_audio.mp4"
        subprocess.run([
            'ffmpeg', '-i', str(concat_video), '-i', str(local_audio_path),
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
            '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-y', str(video_with_audio)
        ], capture_output=True, check=True)
        print("  ✓ Audio")

        if subtitles_generated and ass_path.exists():
            print("🎬 Étape 3/3 : Sous-titres...")
            final_video = tmpdir_path / "final_video.mp4"
            subprocess.run([
                'ffmpeg', '-i', str(video_with_audio),
                '-vf', f"ass={str(ass_path)}",
                '-c:a', 'copy', '-y', str(final_video)
            ], capture_output=True, check=True)
            print("  ✓ Sous-titres")
        else:
            final_video = video_with_audio

        if not final_video.exists() or final_video.stat().st_size == 0:
            print("❌ Vidéo vide")
            return "Error"

        final_size_mb = final_video.stat().st_size / (1024 * 1024)
        print(f"📤 Upload ({final_size_mb:.2f} MB)...")

        final_blob.upload_from_filename(str(final_video), content_type="video/mp4")
        print(f"✅ SUCCÈS !")

    print(f"🎉 TERMINÉ !")
    return "OK"