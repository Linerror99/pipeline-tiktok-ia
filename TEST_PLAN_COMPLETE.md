# Plan de Test Complet - Pipeline V2

## 🎯 Objectif
Valider chaque agent et cloud function avec le workflow total après migration V2.

---

## 📋 Tests par Composant

### 1. ✅ Agent-Script (Gemini 2.5 Pro)

**Fichier de test:** `agent-script/test_simple.py`

**Commande:**
```bash
cd agent-script
python test_simple.py
```

**Vérifications:**
- [x] Gemini génère exactement 5 blocs (pour 36s)
- [x] Format BLOC N (Xs): DIALOGUE / VISUEL
- [x] Parsing regex réussit
- [x] Pas d'astérisques ** dans dialogues
- [x] Durées correctes (8s pour bloc 1, 7s pour les autres)

**Tests supplémentaires:**
```bash
# Test avec durées différentes
python test_simple.py --duration 15  # 2 blocs
python test_simple.py --duration 29  # 4 blocs
python test_simple.py --duration 64  # 9 blocs
```

---

### 2. 🎬 Agent-Video (Veo 3.1 Fast - Génération Parallèle)

**Fichier de test:** `agent-video/test_parallel.py` (à créer)

**Prérequis:**
- Bucket GCS: `gs://tiktok-pipeline-v2-artifacts`
- Firestore collection: `v2_veo_operations`
- Script valide uploadé dans `{video_id}/script_v2.json`

**Test local (simulé):**
```bash
cd agent-video
python test_parallel.py
```

**Test Cloud Run (réel):**
```bash
# Deploy
gcloud run deploy agent-video-v2 \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# Test
curl -X POST https://agent-video-v2-xxx.run.app \
  -H "Content-Type: application/json" \
  -d '{"video_id": "test_20260201_120000"}'
```

**Vérifications:**
- [ ] Lit correctement `script_v2.json` depuis GCS
- [ ] Lance N opérations Veo 3.1 en parallèle (1 par bloc)
- [ ] Stocke `operations = {1: "op1", 2: "op2", ...}`
- [ ] Stocke `clips_status = {1: "generating", ...}`
- [ ] Update Firestore `v2_veo_operations` → `generating_parallel`
- [ ] Retourne liste des operation_names

---

### 3. 🔄 Check-and-Retry-Clips (Monitoring Unifié V1+V2)

**Fichier:** `cloud-functions/check-and-retry-clips/main.py`

**Prérequis:**
- Operations Veo en cours dans Firestore
- Cloud Scheduler configuré (1 minute)

**Test local:**
```bash
cd cloud-functions/check-and-retry-clips
python test_monitor.py
```

**Test Cloud Function:**
```bash
# Deploy
gcloud functions deploy check-and-retry-clips \
  --runtime python311 \
  --trigger-http \
  --region us-central1 \
  --source .

# Test manuel
curl https://us-central1-pipeline-video-ia.cloudfunctions.net/check-and-retry-clips
```

**Vérifications:**
- [ ] Détecte les opérations `generating_parallel` (V2)
- [ ] Vérifie chaque operation dans le dict `operations`
- [ ] Download `block_N.mp4` quand opération terminée
- [ ] Update `clips_status[N] = "completed"`
- [ ] Quand tous blocs completed → appelle agent-assembler
- [ ] Gestion retry (max 3 tentatives)
- [ ] Timeout après 15 minutes

---

### 4. 🎞️ Agent-Assembler (Concat + Sous-titres)

**Fichier de test:** `agent-assembler/test_assembler.py` (à créer)

**Prérequis:**
- Tous les `block_N.mp4` uploadés dans GCS
- FFmpeg installé
- Whisper disponible

**Test local:**
```bash
cd agent-assembler
python test_assembler.py --video-id test_20260201_120000
```

**Vérifications:**
- [ ] Download tous les `block_*.mp4` depuis GCS
- [ ] Concatène dans l'ordre (block_1, block_2, ...)
- [ ] Transcription Whisper depuis vidéo finale
- [ ] Génération fichier `.ass` avec sous-titres
- [ ] Overlay sous-titres avec FFmpeg
- [ ] Upload `final.mp4` vers GCS
- [ ] Update Firestore → `completed`

---

## 🔗 Test Workflow Complet End-to-End

**Fichier:** `test_flow_v2_complete.py` (amélioré)

### Scénario de test
1. **INPUT:** Thème = "Intelligence Artificielle", durée = 36s
2. **ÉTAPE 1:** agent-script génère 5 blocs
3. **ÉTAPE 2:** agent-video lance 5 générations Veo en parallèle
4. **ÉTAPE 3:** check-and-retry surveille et download blocs
5. **ÉTAPE 4:** agent-assembler crée vidéo finale avec sous-titres
6. **OUTPUT:** `final.mp4` disponible dans GCS

### Commande
```bash
python test_flow_v2_complete.py \
  --theme "Intelligence Artificielle" \
  --duration 36 \
  --wait  # Attend completion (peut prendre 10-15 min)
```

### Vérifications finales
- [ ] `script_v2.json` créé dans GCS
- [ ] Firestore `v2_video_status` → `script_generated`
- [ ] Firestore `v2_veo_operations` créé avec 5 operations
- [ ] 5 fichiers `block_1.mp4` ... `block_5.mp4` dans GCS
- [ ] Firestore `clips_status` = {1: "completed", ..., 5: "completed"}
- [ ] `final.mp4` créé avec sous-titres
- [ ] Firestore `v2_video_status` → `completed`
- [ ] Durée finale = ~36s ± 2s

---

## 📊 Critères de Succès Global

### Performance
- ✅ Génération parallèle < 10 min (vs 15+ min séquentiel)
- ✅ Monitoring détecte blocs terminés < 2 min
- ✅ Assemblage final < 2 min

### Fiabilité
- ✅ 0 erreur sur parsing script
- ✅ Retry automatique en cas d'échec Veo
- ✅ Gestion timeout (15 min max)

### Qualité
- ✅ Audio natif Veo 3.1 (lip-sync parfait)
- ✅ Sous-titres synchronisés avec Whisper
- ✅ Vidéo finale lisible sur TikTok (9:16, <60s)

---

## 🚀 Prochaines Étapes

1. **Exécuter test_simple.py** → Valider agent-script ✅
2. **Créer test_parallel.py** → Valider génération parallèle
3. **Créer test_monitor.py** → Valider monitoring
4. **Créer test_assembler.py** → Valider assemblage
5. **Améliorer test_flow_v2.py** → Test end-to-end complet

---

## 📝 Notes

- **Coût:** ~$0.50 par test complet (Veo 3.1 Fast: $0.025/sec * 36s * 5 blocs)
- **Temps:** ~10 minutes par test end-to-end
- **Quota:** Limité à 5 req/min pour Veo 3.1 (génération parallèle OK car async)

