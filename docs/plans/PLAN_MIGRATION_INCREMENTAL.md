# 🔄 Plan de Migration Incrémentale V1 → V2

**Branche actuelle:** `v2_migration`  
**Branche production:** `main` (V1, déployée, intacte)  
**Stratégie:** Modifier progressivement les fichiers existants pour Veo 3.1

---

## 🎯 PRINCIPE

- ✅ **V1 (main)** reste déployée et intacte
- ✅ **V2 (v2_migration)** = modifications du code actuel
- ✅ **Git** trace tout, rollback facile si besoin
- ✅ **Migration fichier par fichier** jusqu'à avoir V2 complète
- ✅ **Déployer V2** en parallèle de V1 quand prête
- ✅ **Supprimer déploiement V1** après validation

---

## 📋 INVENTAIRE DES MODIFICATIONS

### Fichiers à MODIFIER (adapter pour Veo 3.1)

| Fichier | Modifications | Complexité | Ordre |
|---------|---------------|------------|-------|
| **agent-script/main.py** | Format BLOCS avec dialogues | 🟡 Moyen | 1 |
| **agent-audio/main.py** | ⚠️ SUPPRIMER (audio natif Veo 3.1) | 🟢 Facile | - |
| **agent-video/main.py** | Remplacer Veo 3.0 → Veo 3.1 Fast | 🔴 Complex | 2 |
| **monitor-and-assemble/main.py** | Monitoring async Veo operations | 🔴 Complex | 3 |
| **agent-assembler/main.py** | Extraction audio depuis Veo, pas TTS | 🟡 Moyen | 4 |
| **backend/app/services/video_generation.py** | Appels agents V2 | 🟡 Moyen | 5 |
| **backend/app/routers/videos.py** | Endpoints V2 | 🟢 Facile | 6 |
| **frontend/src/pages/CreateVideo.jsx** | UI durée cible, coûts | 🟢 Facile | 7 |
| **deploy.sh** | Noms services *-v2 | 🟢 Facile | 8 |
| **build-and-push.sh** | Images *-v2 | 🟢 Facile | 8 |

### Fichiers à GARDER (inchangés)

- ✅ `backend/app/routers/auth.py` → Bon tel quel
- ✅ `backend/app/models/` → Bon tel quel
- ✅ `backend/app/utils/jwt.py` → Bon tel quel
- ✅ `frontend/src/components/` → Bon tel quel
- ✅ `frontend/src/contexts/AuthContext.jsx` → Bon tel quel
- ✅ `cloud-functions/rotate-access-code/` → Bon tel quel (commun V1/V2)

---

## 🔨 PLAN D'EXÉCUTION (8 Étapes)

---

### **ÉTAPE 1: Adapter agent-script (Format BLOCS)**

**Fichier:** `agent-script/main.py`

**Modifications:**

```python
# AVANT (V1):
def generate_script(theme):
    prompt = f"""
    Crée un script TikTok avec minimum 8 scènes.
    
    SCÈNE 1:
    VISUEL: Description...
    NARRATION: Texte...
    """
    # Parse SCÈNE 1, SCÈNE 2, etc.

# APRÈS (V2):
def generate_script(theme, target_duration=36):
    # Calculer nombre de blocs
    if target_duration <= 8:
        target_blocks = 1
    else:
        target_blocks = 1 + math.ceil((target_duration - 8) / 7)
    
    target_blocks = min(target_blocks, 10)  # Max 10 blocs
    
    prompt = f"""
    Crée un script TikTok sur: {theme}
    
    FORMAT: {target_blocks} BLOCS
    Durée totale: {8 if target_blocks == 1 else 8 + (target_blocks-1)*7}s
    
    BLOC 1 (8s):
    DIALOGUE: "Texte parlé exact par narrateur"
    VISUEL: Description visuelle détaillée scène
    
    BLOC 2 (7s):
    DIALOGUE: "Suite texte parlé..."
    VISUEL: Description continuation
    
    [... jusqu'à BLOC {target_blocks}]
    """
    
    response = gemini_model.generate_content(prompt)
    
    # Parser format BLOCS
    blocks = parse_blocks(response.text)
    
    # Sauvegarder JSON
    script_data = {
        'blocks': blocks,
        'total_duration': 8 if len(blocks) == 1 else 8 + (len(blocks)-1)*7,
        'theme': theme
    }
    
    blob = bucket.blob(f'{video_id}/script_v2.json')
    blob.upload_from_string(json.dumps(script_data))
```

**Fonction helper:**

```python
def parse_blocks(script_text):
    """Parse format BLOC X (Xs): DIALOGUE: ... VISUEL: ..."""
    blocks = []
    
    # Regex pour extraire blocs
    import re
    bloc_pattern = r'BLOC\s+(\d+).*?DIALOGUE:\s*"?([^"]+)"?\s*VISUEL:\s*([^\n]+)'
    
    matches = re.finditer(bloc_pattern, script_text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        bloc_num = int(match.group(1))
        dialogue = match.group(2).strip()
        visuel = match.group(3).strip()
        
        blocks.append({
            'bloc': bloc_num,
            'dialogue': dialogue,
            'visuel': visuel,
            'duration': 8 if bloc_num == 1 else 7
        })
    
    return blocks
```

**Tests:**
```bash
# Tester génération 1 bloc (8s)
python test_script_v2.py --theme "Test court" --duration 8

# Tester génération 5 blocs (36s)
python test_script_v2.py --theme "Test moyen" --duration 36
```

---

### **ÉTAPE 2: Supprimer agent-audio (Audio natif)**

**Action:** Supprimer le dossier `agent-audio/` complètement

```bash
# Audio natif intégré dans Veo 3.1, plus besoin de TTS séparé
rm -rf agent-audio/
```

**Note:** L'audio sera généré directement par Veo 3.1 dans l'étape suivante

---

### **ÉTAPE 3: Remplacer agent-video (Veo 3.0 → Veo 3.1)**

**Fichier:** `agent-video/main.py`

**Modifications majeures:**

```python
# AVANT (V1):
def generate_video_clips(video_id, script):
    # Génère 8 clips Veo 3.0 en parallèle
    # Pas d'audio
    for scene in scenes:
        veo_request = {
            'prompt': scene['visuel'],
            'duration': 4,  # 4s par clip
            'aspect_ratio': '9:16'
        }

# APRÈS (V2):
def generate_veo31_video(video_id):
    """
    Génère BLOC 1 (8s) avec Veo 3.1 Fast + audio natif
    Enregistre operation dans Firestore pour monitoring async
    """
    # Charger script
    script_blob = bucket.blob(f'{video_id}/script_v2.json')
    script = json.loads(script_blob.download_as_text())
    blocks = script['blocks']
    
    # Générer BLOC 1 uniquement
    bloc_1 = blocks[0]
    prompt = f"{bloc_1['visuel']}\n\nDialogue à dire: {bloc_1['dialogue']}"
    
    # Appel Veo 3.1 Fast avec audio natif
    from google.cloud import aiplatform
    from google.cloud.aiplatform_v1beta1 import types
    
    model = aiplatform.preview.GenerativeModel("veo-3.1-fast")
    
    operation = model.generate_videos(
        prompt=prompt,
        config=types.GenerateVideosConfig(
            duration_seconds=8,
            resolution="720p",  # Cohérent avec extensions
            aspect_ratio="9:16",
            generate_audio=True  # Audio natif !
        )
    )
    
    # NE PAS ATTENDRE (async)
    # Enregistrer operation dans Firestore
    firestore_client.collection('v2_veo_operations').document(video_id).set({
        'status': 'generating_block_1',
        'operation_name': operation.name,
        'blocks': blocks,
        'current_block': 1,
        'total_blocks': len(blocks),
        'created_at': firestore.SERVER_TIMESTAMP,
        'video_id': video_id,
        'veo_version': '3.1-fast'
    })
    
    print(f"✅ Veo 3.1 operation lancée: {operation.name}")
    return {'status': 'ok', 'operation_name': operation.name}
```

**Nouveau:** Collection Firestore `v2_veo_operations` pour tracking

---

### **ÉTAPE 4: Adapter monitor-and-assemble (Monitoring Async)**

**Fichier:** `monitor-and-assemble/main.py`

**Renommer:** `monitor-and-assemble/` → `monitor-veo31/`

**Modifications:**

```python
# AVANT (V1):
def monitor_and_assemble(request):
    # Check operations Veo 3.0 (8 clips)
    # Assemble quand tous ready

# APRÈS (V2):
import functions_framework
from google.cloud import aiplatform, firestore, storage
import requests

firestore_client = firestore.Client()
storage_client = storage.Client()
bucket = storage_client.bucket('tiktok-pipeline-v2-artifacts')

@functions_framework.http
def monitor_veo31_operations(request):
    """
    Vérifie opérations Veo 3.1 en cours
    Appelé par Cloud Scheduler chaque minute
    """
    # Récupérer opérations en cours
    operations = firestore_client.collection('v2_veo_operations')\
        .where('status', 'in', [
            'generating_block_1', 
            'generating_block_2', 
            'generating_block_3',
            'generating_block_4',
            'generating_block_5'
        ])\
        .stream()
    
    for op_doc in operations:
        op_data = op_doc.to_dict()
        video_id = op_doc.id
        
        try:
            # Vérifier status operation
            operation = aiplatform.Operation(op_data['operation_name'])
            
            if operation.done:
                if operation.error:
                    handle_veo_failure(video_id, op_data)
                else:
                    handle_veo_success(video_id, op_data, operation)
            else:
                print(f"⏳ {video_id} - Bloc {op_data['current_block']}/{op_data['total_blocks']} en cours")
                
        except Exception as e:
            print(f"❌ Erreur monitoring {video_id}: {e}")
    
    return "OK"

def handle_veo_success(video_id, op_data, operation):
    """Opération réussie → Télécharger et lancer bloc suivant"""
    current_block = op_data['current_block']
    total_blocks = op_data['total_blocks']
    
    # Télécharger vidéo générée
    video_uri = operation.result.generated_videos[0].video.uri
    video_blob = bucket.blob(f'{video_id}/block_{current_block}.mp4')
    
    # Download depuis URI Vertex AI
    import urllib.request
    urllib.request.urlretrieve(video_uri, f'/tmp/block_{current_block}.mp4')
    video_blob.upload_from_filename(f'/tmp/block_{current_block}.mp4')
    
    print(f"✅ Bloc {current_block} téléchargé")
    
    # Si blocs restants → Lancer extension
    if current_block < total_blocks:
        next_block = current_block + 1
        block_data = op_data['blocks'][next_block - 1]
        
        # Générer extension
        model = aiplatform.preview.GenerativeModel("veo-3.1-fast")
        next_operation = model.generate_videos(
            prompt=f"{block_data['visuel']}\n\nDialogue: {block_data['dialogue']}",
            video=types.Video(uri=video_uri),  # Extension depuis vidéo précédente
            config=types.GenerateVideosConfig(
                duration_seconds=7,
                resolution="720p",
                aspect_ratio="9:16",
                generate_audio=True
            )
        )
        
        # Update Firestore
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': f'generating_block_{next_block}',
            'operation_name': next_operation.name,
            'current_block': next_block
        })
        
        print(f"🔄 Bloc {next_block} lancé")
    else:
        # Tous blocs terminés → Déclencher assemblage
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': 'ready_for_assembly'
        })
        
        # Appeler agent-assembler
        requests.post(
            'https://agent-assembler-v2-xxx.run.app',
            json={'video_id': video_id}
        )
        
        print(f"🎬 Assemblage déclenché pour {video_id}")

def handle_veo_failure(video_id, op_data):
    """Gestion échecs avec retry"""
    retry_count = op_data.get('retry_count', 0)
    
    if retry_count < 3:
        # Retry
        print(f"🔄 Retry {retry_count+1}/3 pour {video_id}")
        # ... logique retry
    else:
        # Échec définitif
        firestore_client.collection('v2_veo_operations').document(video_id).update({
            'status': 'failed'
        })
        firestore_client.collection('v2_video_status').document(video_id).update({
            'status': 'error',
            'error_message': 'Génération Veo échouée après 3 tentatives'
        })
```

**Cloud Scheduler:**
```bash
# Créer job Cloud Scheduler 1 minute
gcloud scheduler jobs create http monitor-veo31-scheduler \
    --schedule="* * * * *" \
    --uri="https://monitor-veo31-xxx.run.app" \
    --http-method=POST
```

---

### **ÉTAPE 5: Adapter agent-assembler (Extraction Audio)**

**Fichier:** `agent-assembler/main.py`

**Modifications:**

```python
# AVANT (V1):
def assemble_video(video_id):
    # 1. Concaténer 8 clips vidéo
    # 2. Ajouter audio TTS séparément
    # 3. Whisper sur audio TTS
    # 4. Générer sous-titres

# APRÈS (V2):
def assemble_video_v2(video_id):
    """
    1. Concaténer blocs vidéo (audio déjà inclus)
    2. Extraire audio de la vidéo finale
    3. Whisper sur audio extrait
    4. Générer sous-titres
    """
    # 1. Télécharger tous les blocs
    op_data = firestore_client.collection('v2_veo_operations').document(video_id).get().to_dict()
    total_blocks = op_data['total_blocks']
    
    block_files = []
    for i in range(1, total_blocks + 1):
        blob = bucket.blob(f'{video_id}/block_{i}.mp4')
        local_path = f'/tmp/{video_id}_block_{i}.mp4'
        blob.download_to_filename(local_path)
        block_files.append(local_path)
    
    # 2. Concaténer blocs (FFmpeg)
    concat_list = '/tmp/concat_list.txt'
    with open(concat_list, 'w') as f:
        for block_file in block_files:
            f.write(f"file '{block_file}'\n")
    
    final_no_subs = f'/tmp/{video_id}_final_no_subs.mp4'
    subprocess.run([
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', concat_list,
        '-c', 'copy',
        final_no_subs
    ], check=True)
    
    print(f"✅ Vidéo concaténée: {total_blocks} blocs")
    
    # 3. Extraire audio de la vidéo
    audio_path = f'/tmp/{video_id}_audio.wav'
    subprocess.run([
        'ffmpeg', '-i', final_no_subs,
        '-vn', '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1',
        audio_path
    ], check=True)
    
    print(f"✅ Audio extrait")
    
    # 4. Whisper sur audio extrait (word-level timestamps)
    import whisper
    model = whisper.load_model("base")
    
    result = model.transcribe(
        audio_path,
        language="fr",
        word_timestamps=True
    )
    
    # 5. Générer sous-titres ASS (karaoke)
    ass_path = f'/tmp/{video_id}_subtitles.ass'
    generate_ass_subtitles(result, ass_path)
    
    # 6. Ajouter sous-titres à la vidéo
    final_with_subs = f'/tmp/{video_id}_final.mp4'
    subprocess.run([
        'ffmpeg', '-i', final_no_subs,
        '-vf', f"ass={ass_path}",
        '-c:a', 'copy',
        final_with_subs
    ], check=True)
    
    # 7. Upload final
    final_blob = bucket.blob(f'{video_id}/final.mp4')
    final_blob.upload_from_filename(final_with_subs)
    
    # 8. Update Firestore
    firestore_client.collection('v2_video_status').document(video_id).update({
        'status': 'completed',
        'final_url': final_blob.public_url
    })
    
    print(f"🎉 Vidéo {video_id} terminée")
```

**Différence clé:** Audio extrait de la vidéo Veo, pas TTS séparé

---

### **ÉTAPE 6: Adapter Backend Services**

**Fichier:** `backend/app/services/video_generation.py`

**Modifications:**

```python
# AVANT (V1):
def create_video(theme, user_id):
    # Appelle generate-script-agent (Cloud Function)
    # Qui déclenche cascade V1

# APRÈS (V2):
def create_video_v2(theme, user_id, target_duration=36):
    """Créer vidéo V2 avec Veo 3.1"""
    video_id = str(uuid.uuid4())
    
    # Init Firestore status
    firestore_client.collection('v2_video_status').document(video_id).set({
        'status': 'initializing',
        'user_id': user_id,
        'theme': theme,
        'target_duration': target_duration,
        'created_at': firestore.SERVER_TIMESTAMP
    })
    
    # Appeler agent-script-v2 (Cloud Run)
    response = requests.post(
        SCRIPT_AGENT_V2_URL,  # Cloud Run agent-script
        json={
            'video_id': video_id,
            'theme': theme,
            'target_duration': target_duration
        }
    )
    
    return video_id
```

**Variables env:**
```python
# backend/app/config.py
SCRIPT_AGENT_V2_URL = os.getenv('SCRIPT_AGENT_V2_URL')  # Cloud Run URL
BUCKET_V2_NAME = os.getenv('BUCKET_V2_NAME', 'tiktok-pipeline-v2-artifacts')
```

---

### **ÉTAPE 7: Adapter Frontend**

**Fichier:** `frontend/src/pages/CreateVideo.jsx`

**Modifications:**

```jsx
// Ajouter sélecteur durée
function CreateVideo() {
  const [theme, setTheme] = useState('');
  const [duration, setDuration] = useState(36);
  const [estimatedCost, setEstimatedCost] = useState(null);
  
  useEffect(() => {
    // Calculer coût estimé
    const cost = calculateCost(duration);
    setEstimatedCost(cost);
  }, [duration]);
  
  const calculateCost = (dur) => {
    const veoFastRate = 0.15; // $/sec avec audio
    const scriptCost = 0.002; // Gemini 2.5 Pro
    return (dur * veoFastRate + scriptCost).toFixed(2);
  };
  
  return (
    <div>
      <h1>Créer Vidéo V2</h1>
      
      {/* Sélecteur durée */}
      <div className="mb-4">
        <label>Durée cible:</label>
        <div className="flex gap-2">
          {[8, 36, 60, 78].map(d => (
            <button
              key={d}
              onClick={() => setDuration(d)}
              className={duration === d ? 'bg-blue-600 text-white' : 'bg-gray-200'}
            >
              {d}s
            </button>
          ))}
        </div>
      </div>
      
      {/* Coût estimé */}
      <div className="bg-green-100 p-3 rounded mb-4">
        <p>Coût estimé: ${estimatedCost}</p>
        {parseFloat(estimatedCost) > 10 && (
          <p className="text-red-600">⚠️ Coût élevé</p>
        )}
      </div>
      
      {/* Thème */}
      <textarea
        value={theme}
        onChange={(e) => setTheme(e.target.value)}
        placeholder="Décris ton thème..."
      />
      
      <button onClick={handleCreate}>
        Générer ({duration}s - ${estimatedCost})
      </button>
    </div>
  );
}
```

---

### **ÉTAPE 8: Adapter Scripts Déploiement**

**Fichier:** `build-and-push.sh`

```bash
# Modifier noms images
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/backend-v2:latest"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/frontend-v2:latest"

# Agents
SCRIPT_V2_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/agent-script-v2:latest"
VEO31_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/agent-veo31:latest"
MONITOR_VEO31_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/monitor-veo31:latest"
ASSEMBLER_V2_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/agent-assembler-v2:latest"
```

**Fichier:** `deploy.sh`

```bash
# Déployer services avec noms *-v2
gcloud run deploy pipeline-backend-v2 \
    --image=${BACKEND_V2_IMAGE} \
    # ... reste identique

gcloud run deploy pipeline-frontend-v2 \
    --image=${FRONTEND_V2_IMAGE} \
    # ... reste identique

gcloud run deploy agent-script-v2 ...
gcloud run deploy agent-veo31 ...
gcloud run deploy monitor-veo31 ...
gcloud run deploy agent-assembler-v2 ...
```

---

## ✅ CHECKLIST D'EXÉCUTION

**Phase 1: Modifications Code (Semaines 1-3)**
- [ ] Étape 1: Modifier agent-script (format BLOCS)
- [ ] Étape 2: Supprimer agent-audio
- [ ] Étape 3: Modifier agent-video (Veo 3.1)
- [ ] Étape 4: Créer monitor-veo31 (async)
- [ ] Étape 5: Modifier agent-assembler (extraction audio)
- [ ] Étape 6: Modifier backend services
- [ ] Étape 7: Modifier frontend UI
- [ ] Étape 8: Modifier scripts déploiement

**Phase 2: Tests Locaux (Semaine 4)**
- [ ] Docker Compose avec nouvelles images
- [ ] Tester génération 1 bloc (8s)
- [ ] Tester génération 5 blocs (36s)
- [ ] Vérifier audio natif synchronisé
- [ ] Vérifier sous-titres Whisper

**Phase 3: Déploiement V2 (Semaine 5)**
- [ ] Push images v2_migration vers Artifact Registry
- [ ] Deploy services *-v2 en production
- [ ] Tester avec 5 vidéos réelles
- [ ] Comparer coûts V1 vs V2

**Phase 4: Bascule (Semaine 6-7)**
- [ ] Valider stabilité V2 (7 jours)
- [ ] Supprimer déploiement V1 (main)
- [ ] Merger v2_migration → main
- [ ] Documentation finale

---

## 🚀 COMMANDES RAPIDES

```bash
# Travailler sur v2_migration
git checkout v2_migration
git pull origin v2_migration

# Faire modifications (Étapes 1-8)
# ...

# Commit progressif
git add agent-script/
git commit -m "Étape 1: Format BLOCS pour agent-script"

git add agent-video/
git commit -m "Étape 3: Migration Veo 3.1 Fast"

# ... etc.

# Push régulièrement
git push origin v2_migration

# Déployer V2 quand prêt
./build-and-push.sh  # Build images *-v2
./deploy.sh          # Deploy services *-v2

# Merger dans main après validation
git checkout main
git merge v2_migration
git push origin main
```

---

## 🎯 AVANTAGES MIGRATION INCRÉMENTALE

✅ **Git = filet de sécurité** → Rollback facile si erreur  
✅ **V1 (main) intacte** → Production jamais touchée  
✅ **Modifications progressives** → Tester après chaque étape  
✅ **Garder le bon de V1** → Pas de refonte complète  
✅ **Branche dédiée** → Expérimentation sans risque  

C'est PARFAIT comme approche ! 🎉

Tu veux qu'on commence par quelle étape ? (1-8)
