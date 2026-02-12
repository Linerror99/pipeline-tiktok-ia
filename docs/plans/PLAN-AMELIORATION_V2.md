# 📊 ANALYSE COMPLÈTE DU REPO `pipeline-tiktok-ia`

---

## 🏗️ **ARCHITECTURE GLOBALE**

Tu as créé un **pipeline serverless sur Google Cloud** pour générer automatiquement des vidéos TikTok/Shorts à partir d'un thème textuel. Voici les composants : 

```
┌─────────────────────────────────────────────────────────────────┐
│                      UTILISATEUR (Frontend)                     │
│  • Saisit un thème + code d'accès                              │
│  • Authentification JWT + Firestore                            │
│  • Quota :  2 vidéos/user (admin = illimité)                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP POST /api/videos/create
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│  • Vérifie code d'accès (rotatif, change chaque heure)         │
│  • Vérifie quota utilisateur (Firestore)                       │
│  • Appelle Agent Script                                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│         AGENT 1: Script (Cloud Function HTTP)                  │
│  • Reçoit: {"theme": "Les pandas"}                             │
│  • Appelle Gemini 2.5 Pro pour générer script TikTok           │
│  • Contrainte:  MINIMUM 8 scènes (64-90s de vidéo)              │
│  • Sauvegarde: script_theme.txt → GCS                          │
│  • Format:                                                       │
│    **VISUEL:** description pour IA vidéo                       │
│    **VOIX OFF:** texte narration (sans ** dans le texte)       │
│  • Régénère si < 8 scènes                                      │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Trigger: Fichier script_*. txt uploadé
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│         AGENT 2: Audio (Cloud Function CloudEvent)             │
│  • Lit script_theme.txt depuis GCS                             │
│  • Compte les scènes (VISUEL) → calcul durée cible (8s/scène)  │
│  • Extrait texte VOIX OFF (ignore VISUEL/SCÈNE/DURÉE)          │
│  • Nettoie markdown (**, *)                                    │
│  • Calcule vitesse de parole pour matcher durée cible          │
│    Formule: speed_ratio = (mots / 2. 5) / (scènes × 8)          │
│    Limité:  0.8x - 1.2x pour rester naturel                     │
│  • Appelle Google Text-to-Speech Gemini 2.5 Pro                │
│    Voix: "Rasalgethi" (FR-FR)                                  │
│  • Sauvegarde: audio_theme.mp3 → GCS                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Trigger:  Fichier audio_*.mp3 uploadé
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│         AGENT 3: Vidéo (Cloud Function CloudEvent)             │
│  • Lit script pour extraire prompts visuels                    │
│  • Lance N tâches Veo 3.0 en PARALLÈLE (REST API)              │
│    - Format: 9: 16 (TikTok)                                     │
│    - Durée: 4 secondes/clip                                    │
│    - Style: "Cinematic, photorealistic, vibrant colors"        │
│  • Stockage: gs://bucket/video_clips/theme/clip_N/            │
│  • Crée document Firestore video_status:                        │
│    {                                                            │
│      video_id, status:  "processing",                           │
│      total_clips, completed_clips:  0,                          │
│      clips:  {                                                  │
│        "1": {status: "pending", operation_name, prompt},       │
│        "2": {... }                                              │
│      }                                                          │
│    }                                                            │
│  • IMPORTANT: Préserve l'ordre des scènes via index original   │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Monitoring asynchrone
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│    MONITORING: monitor-and-assemble (Cloud Scheduler 2min)    │
│  • Vérifie toutes les vidéos en status "processing"            │
│  • Pour chaque clip:                                            │
│    - Check opération Veo via API                               │
│    - Si 404 (expiré) → vérifie GCS directement                 │
│    - Si failed → retry (max 3 tentatives)                      │
│    - Si ready → met à jour Firestore                           │
│  • Quand tous clips prêts → appelle Assembleur (HTTP)          │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Trigger HTTP quand tous clips ready
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│      AGENT 4: Assembleur (Cloud Function HTTP)                 │
│  • Reçoit: {"video_id": "theme_123456"}                        │
│  • Télécharge tous les clips depuis GCS (ordre préservé)       │
│  • Télécharge audio_theme.mp3                                  │
│  • GÉNÉRATION SOUS-TITRES WHISPER:                              │
│    1. Transcrit audio avec Whisper (base model)                │
│    2. Extrait timestamps par MOT (word_timestamps=True)        │
│    3. Groupe par 2 mots pour lisibilité                        │
│    4. Effet karaoke:  Blanc → Jaune à 35% de la durée           │
│    5. Format ASS (Advanced SubStation Alpha)                   │
│       - Police: Arial Black, 90pt                              │
│       - Résolution: 1080x1920 (TikTok vertical)                │
│       - Contour noir, ombre portée                             │
│  • ASSEMBLAGE FFMPEG (3 étapes):                               │
│    1. Concaténation clips (concat demuxer)                     │
│    2. Ajout audio (map 0: v + map 1:a)                          │
│    3. Incrustation sous-titres ASS (filter:  ass=)              │
│  • Sauvegarde:  final_theme.mp4 → GCS                           │
│  • Met à jour Firestore:  status = "completed"                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 **SYSTÈME D'AUTHENTIFICATION**

### Code d'accès rotatif
- **Cloud Function** : `rotate-access-code` (Python)
- **Stockage** : Firestore `config/access_code`
- **Rotation** : Cloud Scheduler (toutes les heures)
- **Format** : 8 caractères (uppercase + chiffres, sans O/I/0)
- **Utilisation** : Vérifié lors de l'inscription

### Authentification utilisateur
- **Backend** : FastAPI avec PyJWT + bcrypt
- **Firestore** : Collection `users`
  ```json
  {
    "email": "user@example.com",
    "password_hash": "bcrypt_hash",
    "is_admin": false,
    "video_count": 0,
    "max_videos":  2,  // -1 pour admin = illimité
    "created_at": "timestamp",
    "last_login": "timestamp"
  }
  ```
- **JWT** : Expiration 7 jours, contient user_id + email + is_admin
- **Quota** :  Vérifié AVANT création vidéo, incrémenté APRÈS succès

### Frontend
- React 18 + Vite + Tailwind CSS
- AuthContext (localStorage pour token)
- Routes protégées avec ProtectedRoute
- Navbar affiche quota (ex: "john@email.com (1/2 ✨)")

---

## 📁 **STRUCTURE FIRESTORE**

### Collection `video_status`
Document par vidéo :
```json
{
  "video_id": "theme_123456",
  "status": "processing",  // ou ready_to_assemble, assembling, completed, failed
  "total_clips":  8,
  "completed_clips":  3,
  "bucket_name": "tiktok-pipeline-artifacts-.. .",
  "clips": {
    "1": {
      "status": "ready",
      "operation_name":  "projects/. ../operations/.. .",
      "prompt": "Cinematic panda eating bamboo.. .",
      "retry_count": 0,
      "gcs_uri": "gs://bucket/video_clips/theme/clip_1/video. mp4"
    },
    "2": {... }
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## ⚙️ **TECHNOLOGIES UTILISÉES**

### Backend (Python)
- **Framework** : FastAPI 0.115
- **Auth** : PyJWT 2.8 + bcrypt 4.1 + Firebase Admin 6.4
- **Storage** : google-cloud-storage 2.18
- **Deployment** : Docker multi-stage + Cloud Run

### Agents (Python Cloud Functions Gen 2)
- **Script** : Vertex AI Gemini 2.5 Pro
- **Audio** :  Google Cloud Text-to-Speech Gemini 2.5 Pro (voix Rasalgethi)
- **Vidéo** :  Vertex AI Veo 3.0 (REST API)
- **Assembleur** : FFmpeg + Whisper (base model) + Firestore

### Frontend (JavaScript)
- **Framework** : React 18.3 + Vite 6.0
- **Styling** : Tailwind CSS 3.4
- **Routing** : React Router DOM 7.1
- **HTTP** : Axios 1.7
- **Deployment** : Docker + Nginx

### Infrastructure GCP
- **Compute** :  Cloud Run (backend + frontend) + Cloud Functions Gen 2
- **Storage** :  Cloud Storage (scripts, audio, clips, vidéos finales)
- **Database** : Firestore (users, config, video_status)
- **Orchestration** : Cloud Scheduler (monitoring 2min, rotation code 1h)
- **AI** : Vertex AI (Gemini 2.5 Pro, Veo 3.0)

---

## 🎬 **FLUX COMPLET (Exemple)**

```
Utilisateur entre "Les pandas mignons"
   ↓
Backend vérifie code d'accès + quota → OK
   ↓
Agent Script génère 8 scènes avec Gemini
   → script_les_pandas_mignons.txt
   ↓
Agent Audio génère narration (durée ajustée à 64s)
   → audio_les_pandas_mignons.mp3
   ↓
Agent Vidéo lance 8 clips Veo en parallèle
   → video_clips/les_pandas_mignons/clip_1/ ...  clip_8/
   → Firestore:  status=processing, completed_clips=0
   ↓
Monitor vérifie toutes les 2 minutes
   → Clip 1 ready ✓ (completed_clips=1)
   → Clip 2 failed → retry ↻
   → Clip 3 ready ✓ (completed_clips=2)
   ... après ~10-20 minutes ... 
   → Tous prêts (completed_clips=8)
   → Appelle Assembleur
   ↓
Assembleur télécharge clips + audio
   → Whisper transcrit audio avec timestamps
   → Génère subtitles. ass (effet karaoke blanc→jaune)
   → FFmpeg concat + audio + sous-titres
   → final_les_pandas_mignons.mp4
   → Firestore: status=completed
   ↓
Frontend affiche vidéo (streaming + download)
```

---

## ✅ **POINTS FORTS**

1. **Architecture serverless** : Scalable, pay-per-use
2. **Whisper open-source** : Sous-titres parfaitement synchronisés
3. **Veo 3.0 parallèle** : 8 clips générés en même temps (~10-15min au lieu de 80min)
4. **Monitoring robuste** : Retry automatique, gestion erreurs 404
5. **Authentification sécurisée** : JWT + bcrypt + code rotatif
6. **Quota protection** : Évite explosion budget
7. **Ordre préservé** : Index original dans clips (pas de mélange)
8. **Durée ajustée** : Audio adapté au nombre de scènes (8s/scène)

---

## 🚀 **AMÉLIORATIONS PROPOSÉES**

### 🔥 **PRIORITÉ HAUTE**

#### 1. **WebSocket pour suivi temps réel**
**Problème actuel** : Frontend doit poller `/status` toutes les 5-10s
**Solution** : 
- Backend WebSocket qui écoute Firestore (onSnapshot)
- Événements :  `clip_completed`, `assembly_started`, `video_ready`
- Frontend reçoit mises à jour instantanées

```python
# backend/app/routers/websocket.py
from fastapi import WebSocket
from firebase_admin import firestore

@app.websocket("/ws/video/{video_id}")
async def video_status_ws(websocket: WebSocket, video_id: str):
    await websocket.accept()
    
    # Écouter Firestore
    doc_ref = firestore_client.collection('video_status').document(video_id)
    
    def on_snapshot(doc_snapshot, changes, read_time):
        data = doc_snapshot[0].to_dict()
        asyncio.run(websocket.send_json(data))
    
    doc_watch = doc_ref.on_snapshot(on_snapshot)
```

**Impact** : UX 10x meilleure (barre de progression live)

---

#### 2. **Génération de thumbnails**
**Problème** : Liste vidéos sans preview
**Solution** :
```python
# Dans agent-assembler/main.py (après assemblage)
subprocess.run([
    'ffmpeg', '-i', str(final_video), 
    '-ss', '00:00:02',  # 2ème seconde
    '-vframes', '1',
    '-vf', 'scale=540:960',  # 9:16
    str(tmpdir_path / 'thumbnail. jpg')
])

# Upload thumbnail
thumbnail_blob = bucket.blob(f"thumbnails/{video_id}.jpg")
thumbnail_blob.upload_from_filename(str(tmpdir_path / 'thumbnail.jpg'))
```

**Impact** : Liste vidéos + attractive

---

#### 3. **Extraction durée vidéo**
**Problème** : Frontend affiche `duration:  null`
**Solution** :
```python
# backend/app/services/storage.py
import subprocess, json

def get_video_duration(blob):
    """Extrait durée avec ffprobe"""
    with tempfile.NamedTemporaryFile(suffix='. mp4') as tmp:
        blob.download_to_filename(tmp.name)
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-show_format', 
            '-print_format', 'json', tmp.name
        ], capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
```

**Impact** : Afficher "64s" dans la liste

---

#### 4. **Cache Whisper model**
**Problème actuel** : Whisper recharge à chaque cold start (15-30s)
**Solution** :
```python
# agent-assembler/main.py
import os
os.environ['TRANSFORMERS_CACHE'] = '/tmp/. cache'  # Persistent dans Cloud Run

# Dockerfile
RUN mkdir -p /tmp/.cache && \
    python -c "import whisper; whisper.load_model('base')" && \
    mv ~/. cache/whisper /tmp/.cache/
```

**Impact** : Cold start 30s → 5s

---

#### 5. **Retry intelligent avec backoff exponentiel**
**Problème** : Retry immédiat peut saturer API
**Solution** :
```python
# cloud-functions/monitor-and-assemble/main.py
import time

def retry_clip_with_backoff(clip_data):
    retry_count = clip_data.get('retry_count', 0)
    
    # Backoff:  1min, 3min, 10min
    delays = [60, 180, 600]
    
    if retry_count > 0:
        last_retry = clip_data.get('last_retry_at')
        if datetime.utcnow() - last_retry < timedelta(seconds=delays[retry_count-1]):
            return  # Trop tôt, on attend
    
    # Lancer retry... 
```

**Impact** : Moins de 429 (rate limit)

---

### 🌟 **FONCTIONNALITÉS NOUVELLES**

#### 6. **Templates de style**
**Idée** : Proposer des styles prédéfinis
```python
# Agent Script
STYLES = {
    "cinematic": "Cinematic, dramatic lighting, wide shots",
    "anime": "Anime style, Studio Ghibli inspired, vibrant colors",
    "realistic": "Photorealistic, 4K quality, detailed",
    "sketch": "Pencil sketch, black and white, artistic"
}

# Frontend
<select name="style">
  <option value="cinematic">🎬 Cinématique</option>
  <option value="anime">🎨 Anime</option>
  <option value="realistic">📸 Réaliste</option>
</select>
```

**Impact** : Diversité créative

---

#### 7. **Musique de fond**
**Idée** : Ajouter musique libre de droits
```python
# agent-assembler/main.py

# Télécharger musique depuis GCS (stock de musiques)
music_blob = bucket.blob(f"music/{selected_track}.mp3")
local_music = tmpdir_path / "music. mp3"
music_blob. download_to_filename(str(local_music))

# Mixer avec audio narration
subprocess.run([
    'ffmpeg', '-i', str(local_audio_path), '-i', str(local_music),
    '-filter_complex', '[1:a]volume=0.2[music];[0:a][music]amix=inputs=2:duration=first',
    '-c:a', 'aac', '-y', str(mixed_audio)
])
```

**Impact** : Vidéos + engageantes

---

#### 8. **Historique et favoris**
**Firestore** : 
```json
// Collection users/{user_id}/videos
{
  "video_id": "theme_123",
  "theme": "Les pandas",
  "created_at": "timestamp",
  "is_favorite": false,
  "views": 0
}
```

**Frontend** :
- Onglet "Mes vidéos" vs "Toutes les vidéos"
- Bouton ⭐ pour favoris
- Tri par date/vues

**Impact** : Organisation utilisateur

---

#### 9. **Personnalisation voix**
**Idée** : Choix de la voix TTS
```python
VOICES = {
    "rasalgethi": {"name": "Rasalgethi", "gender": "male"},
    "sabik": {"name": "Sabik", "gender": "female"},
    "gemini-2.5": {"name": "Gemini Default", "gender": "neutral"}
}

# Frontend
<select name="voice">
  <option value="rasalgethi">🎙️ Rasalgethi (Homme)</option>
  <option value="sabik">🎙️ Sabik (Femme)</option>
</select>
```

---

#### 10. **Langue multi-langues**
**Idée** : Générer scripts en EN, ES, DE... 
```python
# Agent Script prompt
language_map = {
    "fr": "Génère en français",
    "en": "Generate in English",
    "es":  "Genera en español"
}

# Agent Audio
voice=texttospeech.VoiceSelectionParams(
    language_code=f"{language}-{country. upper()}",
    name=get_voice_for_language(language)
)
```

**Impact** : Expansion internationale

---

### 🔧 **OPTIMISATIONS TECHNIQUES**

#### 11. **Batch Veo avec priorité**
**Idée** : Générer scènes importantes (début/fin) en priorité
```python
# agent-video/main.py
priority_scenes = [1, 2, len(scenes)-1, len(scenes)]  # Début + Fin

for idx in priority_scenes:
    # Lancer immédiatement
    launch_veo_operation(scenes[idx])

time.sleep(5)  # Laisser démarrer

for idx in range(len(scenes)):
    if idx not in priority_scenes:
        launch_veo_operation(scenes[idx])
```

**Impact** : Assembly démarre dès que clips critiques sont prêts

---

#### 12. **Compression vidéo adaptative**
**Problème** : Vidéos lourdes (100-200 MB)
**Solution** :
```python
# agent-assembler/main.py
subprocess.run([
    'ffmpeg', '-i', str(final_video),
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',  # Compression
    '-c:a', 'aac', '-b:a', '128k',  # Audio réduit
    '-movflags', '+faststart',  # Streaming optimisé
    '-y', str(compressed_video)
])
```

**Impact** : 200MB → 40MB (download 5x plus rapide)

---

#### 13. **Cloud CDN pour streaming**
**Idée** :  Utiliser Cloud CDN devant GCS
```bash
gcloud compute backend-buckets create tiktok-videos \
    --gcs-bucket-name=$BUCKET_NAME \
    --enable-cdn
```

**Impact** : Streaming ultra-rapide worldwide

---

#### 14. **Logs structurés**
**Problème** : Difficile de débugger
**Solution** :
```python
import structlog
logger = structlog.get_logger()

logger.info("clip_generated", 
    video_id=video_id, 
    clip_index=i, 
    duration=4, 
    operation_name=operation_name
)
```

**Impact** : Monitoring + analytics

---

#### 15. **Tests automatisés**
**Idée** : CI/CD avec GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/
```

---

### 💰 **GESTION DES COÛTS**

#### 16. **Alertes budget**
```bash
gcloud billing budgets create \
    --billing-account=$BILLING_ACCOUNT \
    --display-name="TikTok Pipeline" \
    --budget-amount=100 \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90
```

#### 17. **Cache Gemini responses**
**Idée** : Sauvegarder scripts similaires
```python
import hashlib

theme_hash = hashlib.md5(theme.encode()).hexdigest()
cached_script = firestore_client.collection('script_cache').document(theme_hash).get()

if cached_script. exists:
    return cached_script.to_dict()['content']
```

**Impact** : Économie sur API calls

---

## 📈 **MÉTRIQUES À TRACKER**

1. **Durée génération** : Script (2min) + Audio (1min) + Vidéo (15min) + Assembly (3min) = **~21min total**
2. **Taux de réussite clips** : % clips sans retry
3. **Coût par vidéo** : Gemini ($0.02) + TTS ($0.05) + Veo ($0.80) + Storage ($0.01) = **~$0.88/vidéo**
4. **Quota utilisateur** :  Combien utilisent 2/2 vidéos ? 
5. **Erreurs fréquentes** :  Quels prompts échouent ?

---

## 🎯 **ROADMAP SUGGÉRÉE**

### Phase 1 (1-2 semaines)
- ✅ Thumbnails
- ✅ Durée vidéo
- ✅ WebSocket temps réel
- ✅ Cache Whisper

### Phase 2 (2-3 semaines)
- ✅ Templates de style
- ✅ Musique de fond
- ✅ Compression vidéo

### Phase 3 (1 mois)
- ✅ Multi-langues
- ✅ Historique/favoris
- ✅ Cloud CDN

### Phase 4 (Long terme)
- ✅ Tests automatisés
- ✅ Analytics avancés
- ✅ API publique (webhooks)

---
