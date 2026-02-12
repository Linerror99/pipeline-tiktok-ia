# 🎯 PLAN D'ÉVOLUTION PROGRESSIF - PARFAIT ! 

---

## 📅 **PHASE 1 : MIGRATION VEO 3.1 (Thème uniquement)**
**Objectif** : Remplacer le système actuel (8 clips assemblés) par Veo 3.1 (1 vidéo fluide avec audio natif)

## 📅 **PHASE 2 :  SYSTÈME DE PERSONNAGES**
**Objectif** :  Ajouter la possibilité de créer et réutiliser des personnages avec Nano Banana

---

# 🚀 PHASE 1 - MIGRATION VEO 3.1

## Architecture cible

```
Frontend:  Saisie thème → Backend → Agent Script → Agent Veo 3.1 → Agent Assembleur
                                                        ↓
                                            Vidéo 60-90s AVEC AUDIO
                                                        ↓
                                            Whisper → Sous-titres
                                                        ↓
                                            Vidéo finale avec sous-titres
```

---

## 📁 FICHIERS À CRÉER/MODIFIER

### ✅ **1. Agent Script (MODIFIÉ)**

#### `agent-script/main.py`
**Changements** :
- Format script adapté pour Veo 3.1 (blocs de scènes avec dialogues)
- Guidage audio (dialogues entre guillemets, effets sonores)

```python
import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage, firestore
import os

PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = "us-central1"
BUCKET_NAME = os.environ. get("BUCKET_NAME")

vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()
firestore_client = firestore. Client()

@functions_framework.http
def generate_script(request):
    """
    Génère un script optimisé pour Veo 3.1 avec audio natif
    """
    request_json = request.get_json(silent=True)
    if not request_json or "theme" not in request_json: 
        return ("Le thème est manquant.", 400)
    
    theme = request_json["theme"]
    print(f"📝 Thème reçu : {theme}")

    model = GenerativeModel("gemini-2.5-pro")
    
    # ✅ NOUVEAU PROMPT OPTIMISÉ POUR VEO 3.1
    prompt = f"""
Tu es un scénariste expert pour des vidéos TikTok virales optimisées pour Veo 3.1.

Ta tâche est de créer un script captivant de 60-90 secondes sur le thème :  "{theme}"

CONTRAINTES STRICTES :
- Durée totale : 60-90 secondes
- Structure : 4-6 BLOCS de scènes (chaque bloc = 12-15 secondes)
- Ton :  Intrigant, éducatif, captivant
- Audio : Inclure dialogues ET effets sonores

FORMAT EXACT À RESPECTER : 

**BLOC 1 (0-15s) :**
DIALOGUES : "Texte exact entre guillemets" (personnage qui parle)
VISUEL : Description détaillée de ce qui se passe à l'écran
AUDIO :  Effets sonores ambiants (vent, pas, portes, musique, etc.)

**BLOC 2 (15-30s) :**
DIALOGUES : "Autre dialogue..."
VISUEL : Actions et mouvements
AUDIO : Sons d'ambiance

[...  continuer jusqu'à 60-90 secondes]

RÈGLES IMPORTANTES :
1. Les DIALOGUES doivent être entre guillemets "" pour que Veo 3.1 les génère
2. Les EFFETS SONORES doivent être explicites (ex: "porte qui grince", "pas sur le gravier")
3. Les VISUELS doivent être cinématographiques et détaillés
4. Chaque bloc doit faire avancer l'histoire
5. Total : 4-6 blocs minimum

EXEMPLE POUR LE THÈME "Les mystères de l'Égypte ancienne" : 

**BLOC 1 (0-15s) :**
DIALOGUES : Un archéologue murmure "Regardez ces hiéroglyphes...  ils racontent une histoire oubliée."
VISUEL : Travelling avant dans une tombe sombre, torche qui éclaire des murs couverts de hiéroglyphes dorés.  L'archéologue trace les symboles du doigt. 
AUDIO : Écho dans la pierre, respiration légère, crépitement de la torche.

**BLOC 2 (15-30s) :**
DIALOGUES : Une voix off déclare "Les pyramides cachent bien plus que des tombeaux."
VISUEL : Plan large aérien des pyramides de Gizeh au coucher du soleil, caméra qui descend vers l'entrée d'un passage secret.
AUDIO : Vent du désert, sable qui glisse, musique mystérieuse en arrière-plan.

[etc...]

Génère maintenant le script complet pour le thème : "{theme}"
"""

    print("🤖 Génération du script avec Gemini 2.5 Pro...")
    try:
        response = model.generate_content(prompt)
        script_content = response.text
    except Exception as e:
        print(f"❌ Erreur Gemini : {e}")
        return (f"Erreur génération : {e}", 500)

    # ✅ VÉRIFIER LE NOMBRE DE BLOCS
    block_count = script_content.upper().count("**BLOC")
    print(f"📊 Script généré avec {block_count} blocs.")
    
    if block_count < 4:
        print(f"⚠️ Seulement {block_count} blocs. Régénération...")
        prompt_retry = prompt + f"\n\n⚠️ ATTENTION : Tu as généré seulement {block_count} blocs.  RÉGÉNÈRE avec AU MOINS 4 BLOCS (idéalement 5-6)."
        try:
            response = model.generate_content(prompt_retry)
            script_content = response.text
            block_count = script_content.upper().count("**BLOC")
            print(f"✅ Après régénération : {block_count} blocs.")
        except Exception as e: 
            print(f"❌ Erreur régénération : {e}")
    
    # ✅ NOM DE FICHIER
    file_name = f"script_{theme.lower().replace(' ', '_')[:30]}.txt"
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_name)
        blob.upload_from_string(script_content, content_type="text/plain")
    except Exception as e:
        print(f"❌ Erreur sauvegarde : {e}")
        return (f"Erreur sauvegarde : {e}", 500)

    print(f"✅ Script sauvegardé :  {file_name}")
    
    # ✅ CRÉER DOCUMENT FIRESTORE
    video_id = file_name.replace("script_", "").replace(".txt", "")
    firestore_client.collection('video_status').document(video_id).set({
        'video_id': video_id,
        'theme': theme,
        'status':  'script_generated',
        'script_file': file_name,
        'block_count': block_count,
        'created_at': firestore. SERVER_TIMESTAMP
    })

    return (f"✅ Script généré avec {block_count} blocs :  {file_name}", 200)
```

---

### ✅ **2. Agent Vidéo Veo 3.1 (NOUVEAU)**

#### `agent-video-veo31/main.py` (nouveau fichier)

```python
import functions_framework
from google.cloud import storage, firestore
from google import genai
from google.genai import types
import time
import os
import re
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore. Client()
PROJECT_ID = os.environ.get("GCP_PROJECT")

@functions_framework.cloud_event
def generate_video_veo31(cloudevent):
    """
    Génère une vidéo longue avec Veo 3.1 (8s initial + extensions successives)
    Déclenché par l'upload d'un fichier script_*. txt
    """
    data = cloudevent.data
    bucket_name = data["bucket"]
    script_file_name = data["name"]

    print(f"🎬 Déclencheur reçu : {script_file_name}")

    # Filtrer uniquement les scripts
    if not script_file_name.startswith("script_") or not script_file_name. endswith(".txt"):
        print(f"❌ Fichier ignoré (pas un script)")
        return "OK"

    try:
        bucket = storage_client.bucket(bucket_name)
        script_blob = bucket.blob(script_file_name)
        
        if not script_blob.exists():
            print(f"❌ Script non trouvé")
            return "Error"
        
        script_content = script_blob.download_as_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Erreur lecture script : {e}")
        return "Error"

    print(f"📄 Script chargé ({len(script_content)} caractères)")

    # ✅ EXTRAIRE LES BLOCS
    blocks = extract_blocks(script_content)
    
    if not blocks:
        print("❌ Aucun bloc détecté dans le script")
        return "Error"
    
    print(f"📊 {len(blocks)} blocs extraits")
    
    # ID de la vidéo
    video_id = script_file_name.replace("script_", "").replace(".txt", "")
    
    # ✅ INITIALISER GEMINI CLIENT
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")  # Configurer dans Cloud Function
    )
    
    # ✅ BLOC 1 :  Générer vidéo initiale (8s)
    first_block = blocks[0]
    print(f"\n🎥 BLOC 1/{ len(blocks)} :  Génération initiale (8s)")
    print(f"   Prompt : {first_block[: 80]}...")
    
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=first_block,
            config=types.GenerateVideosConfig(
                duration_seconds=8,
                resolution="1080p",
                aspect_ratio="9:16",
                person_generation="allow_all"
            )
        )
        
        # Polling :  attendre que la vidéo soit prête
        while not operation.done: 
            print(f"   ⏳ Génération en cours...")
            time.sleep(15)
            operation = client.operations.get(operation)
        
        if not operation.response or not operation.response.generated_videos:
            print(f"   ❌ Aucune vidéo générée pour le bloc 1")
            return "Error"
        
        current_video = operation.response.generated_videos[0]. video
        print(f"   ✅ Bloc 1 généré (durée:  ~8s)")
        
    except Exception as e:
        print(f"   ❌ Erreur génération bloc 1 : {e}")
        
        # Mettre à jour Firestore
        firestore_client.collection('video_status').document(video_id).update({
            'status': 'failed',
            'error':  str(e)
        })
        return "Error"
    
    # ✅ BLOCS 2-N : Extensions successives (7s chacune)
    for i, block_prompt in enumerate(blocks[1:], start=2):
        print(f"\n🎥 BLOC {i}/{len(blocks)} : Extension (+7s)")
        print(f"   Prompt : {block_prompt[:80]}...")
        
        try:
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                video=current_video,  # ✅ Vidéo précédente comme input
                prompt=block_prompt,
                config=types.GenerateVideosConfig(
                    resolution="720p"  # Extensions = 720p uniquement
                )
            )
            
            # Polling
            while not operation.done:
                print(f"   ⏳ Extension en cours...")
                time.sleep(15)
                operation = client.operations.get(operation)
            
            if not operation.response or not operation.response.generated_videos:
                print(f"   ⚠️ Échec extension bloc {i}, on continue...")
                break
            
            current_video = operation.response.generated_videos[0].video
            print(f"   ✅ Bloc {i} ajouté (~{8 + (i-1)*7}s total)")
            
        except Exception as e:
            print(f"   ⚠️ Erreur extension bloc {i} : {e}")
            print(f"   → On s'arrête ici, vidéo de {8 + (i-2)*7}s")
            break
    
    # ✅ TÉLÉCHARGER ET SAUVEGARDER LA VIDÉO FINALE
    print(f"\n📥 Téléchargement de la vidéo finale...")
    
    try:
        # Télécharger dans /tmp
        temp_video_path = f"/tmp/{video_id}.mp4"
        client.files.download(file=current_video, path=temp_video_path)
        
        print(f"   ✓ Vidéo téléchargée : {os.path.getsize(temp_video_path) / (1024*1024):.2f} MB")
        
        # Upload vers GCS
        veo_video_blob = bucket.blob(f"veo31_videos/{video_id}.mp4")
        veo_video_blob.upload_from_filename(temp_video_path, content_type="video/mp4")
        
        veo_video_uri = f"gs://{bucket_name}/veo31_videos/{video_id}.mp4"
        print(f"   ✓ Uploadé :  {veo_video_uri}")
        
        # Nettoyer /tmp
        os.remove(temp_video_path)
        
    except Exception as e:
        print(f"❌ Erreur téléchargement/upload : {e}")
        
        firestore_client.collection('video_status').document(video_id).update({
            'status': 'failed',
            'error':  f"Download/upload error: {str(e)}"
        })
        return "Error"
    
    # ✅ METTRE À JOUR FIRESTORE
    firestore_client.collection('video_status').document(video_id).update({
        'status': 'video_generated',
        'veo31_video_uri': veo_video_uri,
        'blocks_generated': i if 'i' in locals() else 1,
        'updated_at': datetime.utcnow()
    })
    
    print(f"\n🎉 VIDÉO COMPLÈTE GÉNÉRÉE !")
    print(f"   Blocs : {i if 'i' in locals() else 1}/{len(blocks)}")
    print(f"   Durée estimée : ~{8 + (i-1 if 'i' in locals() else 0)*7}s")
    print(f"   URI : {veo_video_uri}")
    
    return "OK"


def extract_blocks(script_content):
    """
    Extrait les blocs de scènes du script
    
    Format attendu :
    **BLOC 1 (0-15s) :**
    DIALOGUES :  "..."
    VISUEL : ... 
    AUDIO : ...
    
    Returns :  Liste de prompts complets (1 par bloc)
    """
    blocks = []
    current_block = ""
    in_block = False
    
    for line in script_content.splitlines():
        line_upper = line.strip().upper()
        
        # Détecter début de bloc
        if line_upper. startswith("**BLOC") and ":" in line_upper:
            # Sauvegarder le bloc précédent
            if current_block. strip():
                blocks.append(current_block.strip())
            
            current_block = ""
            in_block = True
        
        # Détecter fin de bloc (ligne vide ou nouveau **BLOC)
        elif in_block and (not line.strip() or line_upper.startswith("**BLOC")):
            if current_block.strip():
                blocks.append(current_block. strip())
                current_block = ""
            
            if line_upper.startswith("**BLOC"):
                current_block = ""
                in_block = True
        
        # Ajouter la ligne au bloc actuel
        elif in_block:
            current_block += line + "\n"
    
    # Dernier bloc
    if current_block.strip():
        blocks.append(current_block.strip())
    
    return blocks
```

#### `agent-video-veo31/requirements.txt`
```
functions-framework==3.*
google-cloud-storage==2.18.0
google-cloud-firestore==2.18.0
google-genai==0.3.0
```

#### `agent-video-veo31/Dockerfile`
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8080
ENV FUNCTION_TARGET=generate_video_veo31

CMD exec functions-framework --target=generate_video_veo31 --signature-type=cloudevent
```

---

### ✅ **3. Agent Assembleur (MODIFIÉ)**

#### `agent-assembler/main.py`
**Changements** :
- Télécharger vidéo Veo 3.1 (au lieu de clips multiples)
- Extraire audio de cette vidéo
- Whisper sur cet audio
- Incruster sous-titres

```python
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

# Variable globale pour Whisper
WHISPER_MODEL = None

def get_whisper_model():
    """Charge le modèle Whisper (cache)"""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        print("📦 Chargement Whisper (base)...")
        WHISPER_MODEL = whisper.load_model("base")
        print("  ✓ Modèle chargé")
    return WHISPER_MODEL

def generate_whisper_subtitles(audio_path, output_ass_path):
    """Génère sous-titres ASS avec Whisper"""
    print("🎙️ Transcription Whisper...")
    
    model = get_whisper_model()
    
    result = model.transcribe(
        audio_path,
        language="fr",
        word_timestamps=True,
        verbose=False
    )
    
    print(f"  ✓ Transcription terminée")
    
    # En-tête ASS
    ass_header = """[Script Info]
Title: TikTok Veo 3.1 Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style:  Default,Arial Black,90,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,10,10,80,1
Style:  Highlight,Arial Black,95,&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,7,3,2,10,10,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_events = []
    
    # Extraire mots
    all_words = []
    for segment in result["segments"]:
        if "words" in segment:
            for word_data in segment["words"]:
                all_words.append({
                    "word": word_data["word"]. strip(),
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
        
        start_time = segment[0]['start']
        end_time = segment[-1]['end']
        
        start_time = max(0, start_time - 0.05)
        end_time = max(start_time + 0.1, end_time - 0.05)
        
        text = " ".join([w['word']. upper() for w in segment])
        
        highlight_point = start_time + (end_time - start_time) * 0.35
        
        start_ass = format_timestamp_ass(start_time)
        highlight_ass = format_timestamp_ass(highlight_point)
        end_ass = format_timestamp_ass(end_time)
        
        ass_events.append(f"Dialogue: 0,{start_ass},{highlight_ass},Default,,0,0,0,,{text}")
        ass_events.append(f"Dialogue: 0,{highlight_ass},{end_ass},Highlight,,0,0,0,,{text}")
    
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_header)
        f.write("\n". join(ass_events))
    
    print(f"  ✓ {len(ass_events)} événements ASS générés")
    return True

def format_timestamp_ass(seconds):
    """Convertit secondes en format ASS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)
    return f"{hours}:{minutes: 02d}:{secs:02d}.{centisecs:02d}"

@functions_framework.http
def assemble_video(request):
    """
    Assemble vidéo Veo 3.1 + sous-titres Whisper
    Déclenché par HTTP avec {"video_id": "..."}
    """
    request_json = request.get_json(silent=True)
    
    if not request_json or 'video_id' not in request_json:
        return {"error": "Missing video_id"}, 400
    
    video_id = request_json['video_id']
    
    print(f"🎬 Assemblage pour :  {video_id}")
    
    # Récupérer infos Firestore
    video_doc = firestore_client.collection('video_status').document(video_id).get()
    
    if not video_doc.exists:
        print(f"❌ Document video_status introuvable")
        return {"error": "Video status not found"}, 404
    
    video_data = video_doc.to_dict()
    veo_video_uri = video_data. get('veo31_video_uri')
    bucket_name = veo_video_uri.split('/')[2] if veo_video_uri else None
    
    if not veo_video_uri or not bucket_name:
        print(f"❌ Vidéo Veo 3.1 non trouvée")
        return {"error": "Veo video not found"}, 404
    
    bucket = storage_client.bucket(bucket_name)
    
    print("🎉 Démarrage assemblage...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # ✅ TÉLÉCHARGER VIDÉO VEO 3.1
        print("📥 Téléchargement vidéo Veo 3.1...")
        veo_video_path = tmpdir_path / "veo31_video.mp4"
        
        veo_blob_name = veo_video_uri.replace(f"gs://{bucket_name}/", "")
        veo_blob = bucket.blob(veo_blob_name)
        veo_blob.download_to_filename(str(veo_video_path))
        
        print(f"  ✓ Vidéo téléchargée ({veo_video_path. stat().st_size / (1024*1024):.2f} MB)")
        
        # ✅ EXTRAIRE L'AUDIO
        print("🎵 Extraction audio...")
        audio_path = tmpdir_path / "extracted_audio.mp3"
        
        try:
            subprocess.run([
                'ffmpeg', '-i', str(veo_video_path),
                '-vn',  # Pas de vidéo
                '-acodec', 'mp3',
                '-ar', '16000',  # Sample rate pour Whisper
                '-ac', '1',  # Mono
                '-y', str(audio_path)
            ], capture_output=True, check=True, text=True)
            
            print(f"  ✓ Audio extrait ({audio_path.stat().st_size / (1024*1024):.2f} MB)")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur extraction audio : {e. stderr}")
            return {"error":  "Audio extraction failed"}, 500
        
        # ✅ GÉNÉRER SOUS-TITRES
        ass_path = tmpdir_path / "subtitles.ass"
        subtitles_ok = generate_whisper_subtitles(str(audio_path), str(ass_path))
        
        # ✅ INCRUSTER SOUS-TITRES
        if subtitles_ok and ass_path.exists():
            print("🎬 Incrustation sous-titres...")
            final_video = tmpdir_path / "final_video.mp4"
            
            try:
                subprocess.run([
                    'ffmpeg', '-i', str(veo_video_path),
                    '-vf', f"ass={str(ass_path)}",
                    '-c:a', 'copy',  # Garder l'audio original
                    '-y', str(final_video)
                ], capture_output=True, check=True, text=True)
                
                print("  ✓ Sous-titres incrustés")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Erreur sous-titres : {e.stderr[-300:]}")
                final_video = veo_video_path
        else:
            print("⚠️ Pas de sous-titres, vidéo sans sous-titres")
            final_video = veo_video_path
        
        # Vérifier taille
        if not final_video.exists() or final_video.stat().st_size == 0:
            print("❌ Vidéo finale vide")
            return {"error":  "Final video is empty"}, 500
        
        final_size_mb = final_video.stat().st_size / (1024 * 1024)
        print(f"📤 Upload vidéo finale ({final_size_mb:.2f} MB)...")
        
        # ✅ UPLOAD
        try:
            final_blob_name = f"final_{video_id}.mp4"
            final_blob = bucket. blob(final_blob_name)
            final_blob.upload_from_filename(str(final_video), content_type="video/mp4")
            
            final_video_url = f"gs://{bucket_name}/{final_blob_name}"
            print(f"✅ SUCCÈS : {final_video_url}")
            
            # Mettre à jour Firestore
            firestore_client.collection('video_status').document(video_id).update({
                'status':  'completed',
                'final_video_url': final_video_url,
                'updated_at': datetime.utcnow()
            })
            
        except Exception as e:
            print(f"❌ Erreur upload : {e}")
            
            firestore_client.collection('video_status').document(video_id).update({
                'status': 'failed',
                'error': str(e),
                'updated_at': datetime.utcnow()
            })
            
            return {"error": f"Upload error: {str(e)}"}, 500
    
    print(f"🎉 ASSEMBLAGE TERMINÉ !")
    
    return {
        "status": "success",
        "video_id":  video_id,
        "final_video_url": final_video_url
    }, 200
```

---

### ✅ **4.  Monitoring (MODIFIÉ)**

#### `cloud-functions/monitor-and-assemble/main.py`

**Changements** :
- Surveiller `status = 'video_generated'` au lieu de vérifier clips individuels
- Appeler assembleur quand vidéo Veo 3.1 prête

```python
import functions_framework
from google.cloud import firestore
import requests
import os
from datetime import datetime

firestore_client = firestore.Client()
AGENT_ASSEMBLER_URL = os.environ.get('AGENT_ASSEMBLER_URL', '')

@functions_framework.http
def monitor_and_assemble(request):
    """
    Vérifie les vidéos en status 'video_generated' et déclenche l'assembleur
    """
    print("🔍 === Monitoring vidéos Veo 3.1 ===\n")
    
    videos_ref = firestore_client.collection('video_status')
    ready_videos = videos_ref.where('status', '==', 'video_generated').stream()
    
    checked = 0
    triggered = 0
    
    for video_doc in ready_videos:
        checked += 1
        video_data = video_doc.to_dict()
        video_id = video_data['video_id']
        
        print(f"📹 Vidéo :  {video_id}")
        print(f"   Status : {video_data['status']}")
        print(f"   Veo URI : {video_data.get('veo31_video_uri', 'N/A')}")
        
        # ✅ DÉCLENCHER L'ASSEMBLEUR
        if trigger_assembler(video_id):
            video_doc.reference.update({
                'status': 'assembling',
                'updated_at': datetime.utcnow()
            })
            triggered += 1
            print(f"   ✅ Assembleur déclenché\n")
        else:
            print(f"   ❌ Échec déclenchement\n")
    
    if checked == 0:
        print("ℹ️ Aucune vidéo prête\n")
    
    result = {
        'checked_videos': checked,
        'triggered_assemblies': triggered,
        'message': f"Vérifié {checked} vidéo(s), déclenché {triggered} assemblage(s)"
    }
    
    print(f"✅ {result['message']}")
    return result, 200

def trigger_assembler(video_id):
    """Déclenche l'agent assembleur"""
    try:
        if not AGENT_ASSEMBLER_URL:
            print(f"    ⚠️ AGENT_ASSEMBLER_URL non configurée")
            return False
        
        print(f"    📞 Appel assembleur :  {AGENT_ASSEMBLER_URL}")
        
        response = requests. post(
            AGENT_ASSEMBLER_URL,
            json={"video_id": video_id},
            headers={"Content-Type": "application/json"},
            timeout=600  # 10 minutes
        )
        
        if response. status_code == 200:
            return True
        else:
            print(f"      ❌ Erreur : {response.status_code}")
            print(f"         {response.text[: 200]}")
            return False
            
    except Exception as e: 
        print(f"    ❌ Erreur :  {e}")
        return False
```

---

## 📋 **SCRIPTS DE DÉPLOIEMENT**

### `deploy-veo31.sh` (NOUVEAU)
```bash
#!/bin/bash

PROJECT_ID="pipeline-video-ia"
REGION="us-central1"
BUCKET_NAME="tiktok-pipeline-artifacts-pipeline-video-ia"
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"  # À configurer

echo "🚀 Déploiement Pipeline Veo 3.1..."

# 1. Déployer Agent Script (HTTP)
echo "\n📝 Déploiement agent-script..."
gcloud functions deploy agent-script-veo31 \
    --gen2 \
    --runtime=python312 \
    --region=$REGION \
    --source=./agent-script \
    --entry-point=generate_script \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=300s \
    --memory=512Mi \
    --set-env-vars="GCP_PROJECT=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME"

# 2. Déployer Agent Vidéo Veo 3.1 (CloudEvent sur GCS)
echo "\n🎥 Déploiement agent-video-veo31..."
gcloud functions deploy agent-video-veo31 \
    --gen2 \
    --runtime=python312 \
    --region=$REGION \
    --source=./agent-video-veo31 \
    --entry-point=generate_video_veo31 \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=$BUCKET_NAME" \
    --timeout=3600s \
    --memory=2Gi \
    --set-env-vars="GCP_PROJECT=$PROJECT_ID,GEMINI_API_KEY=$GEMINI_API_KEY"

# 3. Déployer Agent Assembleur (HTTP)
echo "\n🎬 Déploiement agent-assembler..."
gcloud functions deploy agent-assembler-veo31 \
    --gen2 \
    --runtime=python312 \
    --region=$REGION \
    --source=./agent-assembler \
    --entry-point=assemble_video \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=600s \
    --memory=4Gi

ASSEMBLER_URL=$(gcloud functions describe agent-assembler-veo31 --gen2 --region=$REGION --format='value(serviceConfig.uri)')

# 4. Déployer Monitor (HTTP)
echo "\n👁️ Déploiement monitor..."
gcloud functions deploy monitor-and-assemble-veo31 \
    --gen2 \
    --runtime=python312 \
    --region=$REGION \
    --source=./cloud-functions/monitor-and-assemble \
    --entry-point=monitor_and_assemble \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=512Mi \
    --set-env-vars="AGENT_ASSEMBLER_URL=$ASSEMBLER_URL"

MONITOR_URL=$(gcloud functions describe monitor-and-assemble-veo31 --gen2 --region=$REGION --format='value(serviceConfig.uri)')

# 5. Configurer Cloud Scheduler (2 minutes)
echo "\n⏰ Configuration Cloud Scheduler..."
gcloud scheduler jobs create http monitor-veo31-job \
    --location=$REGION \
    --schedule="*/2 * * * *" \
    --uri="$MONITOR_URL" \
    --http-method=POST \
    --description="Vérifie vidéos Veo 3.1 et déclenche assembleur" \
    || echo "Job scheduler existe déjà"

echo "\n✅ DÉPLOIEMENT TERMINÉ !"
echo "\n📋 URLs :"
echo "  Script Agent :  $(gcloud functions describe agent-script-veo31 --gen2 --region=$REGION --format='value(serviceConfig.uri)')"
echo "  Monitor : $MONITOR_URL"
echo "  Assembleur : $ASSEMBLER_URL"
```

---

## 🧪 **TESTS**

### Test complet
```bash
# 1. Générer script
curl -X POST https://agent-script-veo31-xxx.run.app \
  -H "Content-Type: application/json" \
  -d '{"theme":  "Les mystères de l'Égypte ancienne"}'

# 2. Vérifier dans Firestore que status = 'script_generated'

# 3. L'agent vidéo se déclenche automatiquement (upload script_*. txt)

# 4. Après 20-30 min, status = 'video_generated'

# 5. Le monitor déclenche l'assembleur (toutes les 2 min)

# 6. Après 5-10 min, status = 'completed'

# 7. Télécharger la vidéo finale
gsutil cp gs://tiktok-pipeline-artifacts-pipeline-video-ia/final_*. mp4 ./
```

---

## 📊 **COMPARAISON AVANT/APRÈS**

| Aspect | AVANT (8 clips) | APRÈS (Veo 3.1) |
|--------|-----------------|-----------------|
| **Nombre de clips** | 8 clips séparés | 1 vidéo fluide |
| **Audio** | TTS séparé (désynchronisé) | Audio natif Veo (parfait) |
| **Durée totale** | 32-64s | 60-90s |
| **Temps génération** | ~15-20 min | ~25-30 min |
| **Coût** | ~$0.80 | ~$1.50-2.00 |
| **Synchronisation** | ⚠️ Problématique | ✅ Parfaite |
| **Qualité audio** | 🤖 Robotique | 🎤 Naturelle |
| **Transitions** | ❌ Coupures | ✅ Fluides |

---

## ✅ **RÉSUMÉ PHASE 1**

**Ce qu'on fait** :
1. ✅ Modifier `agent-script` pour générer scripts avec dialogues
2. ✅ Créer `agent-video-veo31` pour Veo 3.1 avec extensions
3. ✅ Modifier `agent-assembler` pour extraire audio + Whisper
4. ✅ Modifier `monitor` pour déclencher sur `video_generated`
5. ✅ Déployer tout avec `deploy-veo31.sh`

**Résultat** :
- Frontend inchangé (même interface)
- Utilisateur saisit thème
- Vidéo 60-90s générée automatiquement avec audio natif + sous-titres
- Qualité cinématographique

---
