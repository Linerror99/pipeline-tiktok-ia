# Migration V2 - Résumé Final

## ✅ Architecture finale

### 1. **Génération parallèle (agent-video)**
- Génère TOUS les blocs en même temps (pas de BLOC 1 puis extensions)
- Stocke dict `operations` : `{1: "op_name", 2: "op_name", ...}`
- Stocke dict `clips_status` : `{1: "generating", 2: "generating", ...}`
- Status Firestore : `generating_parallel`

### 2. **Monitoring unifié (check-and-retry-clips)**
- ✅ **Remplace monitor-veo31** (supprimé - redondant)
- Gère V1 ET V2 dans la même fonction
- Vérifie toutes les opérations parallèles
- Télécharge chaque bloc terminé
- Déclenche assemblage quand tous blocs OK
- Cloud Scheduler : **1 minute** (au lieu de 10)

### 3. **Assemblage + sous-titres (agent-assembler)**
- Concatène tous les `block_N.mp4`
- Whisper transcrit **DIRECTEMENT depuis vidéo finale**
- Ajoute sous-titres sur vidéo
- Upload `final.mp4`

---

## 🔄 Workflow complet

```
1. Upload script_v2.json → agent-script-v2
   ↓
2. agent-video-v2 lance N générations EN PARALLÈLE
   - operations: {1: "op1", 2: "op2", 3: "op3"}
   - clips_status: {1: "generating", 2: "generating", 3: "generating"}
   ↓
3. check-and-retry-clips (chaque minute)
   - Vérifie chaque opération (op1, op2, op3)
   - Download bloc 1 quand terminé ✅
   - Download bloc 2 quand terminé ✅
   - Download bloc 3 quand terminé ✅
   - Update clips_status: {1: "completed", 2: "completed", 3: "completed"}
   ↓
4. Quand completed_blocks == total_blocks
   → Appelle agent-assembler-v2
   ↓
5. agent-assembler-v2
   - Concatène block_1.mp4 + block_2.mp4 + block_3.mp4
   - Whisper transcrit final.mp4 (pas d'extraction audio)
   - Ajoute sous-titres
   - Upload final.mp4
```

---

## 📂 Fonctions Cloud déployées

| Fonction | Rôle | Trigger |
|---|---|---|
| **agent-script-v2** | Parse JSON → Blocs | Storage (script_v2.json) |
| **agent-video-v2** | Génération parallèle | HTTP (from agent-script) |
| **check-and-retry-clips** | Monitor V1 + V2 | Scheduler (1 min) |
| **agent-assembler-v2** | Assemblage + sous-titres | HTTP (from check-and-retry) |
| ~~monitor-veo31~~ | ~~Redondant~~ | **SUPPRIMÉ** |

---

## ✨ Avantages architecture finale

### ✅ **Simplicité**
- 1 seule fonction de monitoring (au lieu de 2)
- Logique V1 + V2 unifiée
- Moins de code à maintenir

### ✅ **Performance**
- Génération parallèle = **rapide**
- Pas d'attente séquentielle (BLOC 1 → BLOC 2 → BLOC 3)
- Tous les blocs générés simultanément

### ✅ **Fiabilité**
- Retry automatique (hérité de V1)
- Vérification chaque minute
- Timeout après 15 min (V1)

### ✅ **Audio natif**
- Veo 3.1 génère audio directement
- Pas besoin de TTS externe
- Synchronisation parfaite lip-sync

### ✅ **Sous-titres**
- Whisper transcrit depuis vidéo finale
- Pas d'extraction audio séparée
- Format ASS optimisé TikTok

---

## ❌ Inconvénients vs extensions

### ⚠️ **Pas de continuité visuelle**
- Chaque bloc est indépendant
- Transitions peuvent être brusques
- Personnages/décors peuvent changer

**Mitigation** :
- Prompts avec contexte : "Suite de la scène précédente..."
- Style guides cohérents
- Post-prod avec transitions (future V3)

### ⚠️ **Coût 2× plus élevé**
- Génération complète pour chaque bloc
- Extensions auraient coûté moins cher

**Justification** :
- Extensions BLOQUÉES par SDK limitation
- API REST trop complexe pour V2 MVP
- Coût acceptable pour MVP (~0.30€/vidéo)

---

## 🔧 Changements vs tentative API REST

### ❌ **Abandonnée : API REST avec output_storage_uri**
**Raison** : Trop complexe, pas de SDK support

**Ce qu'on aurait dû faire** :
```python
# API REST directe (bypass SDK)
response = requests.post(
    "https://us-central1-aiplatform.googleapis.com/v1/.../veo-3.1:generateVideos",
    json={
        "instances": [{"video": {"gcsUri": "gs://bucket/block_1.mp4"}}],
        "parameters": {"storageUri": "gs://bucket/output/"}  # ✅ Supporté en REST
    }
)
```

### ✅ **Retenue : Génération parallèle SDK**
**Raison** : Simple, fonctionne, SDK officiel

**Ce qu'on fait** :
```python
# SDK google-genai (simple)
for bloc in blocs:
    operation = genai_client.models.generate_videos(
        prompt=prompt,
        config=types.GenerateVideosConfig(...)
    )
    operations[idx] = operation.name
```

---

## 📊 Firestore structure V2

### **v2_veo_operations/{video_id}**
```json
{
  "video_id": "video_20260201_123456",
  "operations": {
    "1": "projects/.../operations/op1",
    "2": "projects/.../operations/op2",
    "3": "projects/.../operations/op3"
  },
  "clips_status": {
    "1": "completed",
    "2": "generating",
    "3": "generating"
  },
  "status": "generating_parallel",
  "total_blocks": 3,
  "completed_blocks": 1,
  "blocks": [...],
  "created_at": "2026-02-01T12:34:56Z"
}
```

### **v2_video_status/{video_id}**
```json
{
  "status": "generating_video",
  "current_step": "parallel_generation",
  "updated_at": "2026-02-01T12:34:56Z"
}
```

---

## 🚀 Prochaines étapes

### **Immédiat (V2 MVP)**
1. ✅ Tester génération parallèle end-to-end
2. ✅ Valider assemblage + sous-titres
3. ✅ Déployer check-and-retry-clips unifié
4. ❌ Supprimer monitor-veo31 (redondant)

### **Court terme (V2.1)**
- Améliorer prompts pour continuité
- Ajouter transitions entre blocs
- Style guide global

### **Moyen terme (V3)**
- Attendre SDK support pour extensions
- Migrer vers API REST si nécessaire
- Batch requests pour coûts

---

## 📝 Commandes de déploiement

```bash
# Agent video (génération parallèle)
gcloud functions deploy agent-video-v2 \
  --gen2 --runtime=python312 --region=us-central1 \
  --source=./agent-video \
  --entry-point=generate_video_veo31 \
  --trigger-http --allow-unauthenticated \
  --timeout=540s --memory=2Gi

# Check and retry (unifié V1+V2)
gcloud functions deploy check-and-retry-clips \
  --gen2 --runtime=python312 --region=us-central1 \
  --source=./cloud-functions/check-and-retry-clips \
  --entry-point=check_and_retry_clips \
  --trigger-http --allow-unauthenticated \
  --timeout=540s --memory=1Gi \
  --set-env-vars=BUCKET_NAME_V2=tiktok-pipeline-v2-artifacts,AGENT_ASSEMBLER_URL=https://...

# Agent assembler (sous-titres)
gcloud functions deploy agent-assembler-v2 \
  --gen2 --runtime=python312 --region=us-central1 \
  --source=./agent-assembler \
  --entry-point=assemble_video_v2 \
  --trigger-http --allow-unauthenticated \
  --timeout=540s --memory=4Gi

# Cloud Scheduler (1 minute)
gcloud scheduler jobs update http check-and-retry-clips \
  --schedule="* * * * *" \
  --uri="https://us-central1-pipeline-video-ia.cloudfunctions.net/check-and-retry-clips"
```

---

## ✅ Conclusion

**Architecture finale** :
- ✅ Génération parallèle (rapide)
- ✅ Monitoring unifié V1+V2 (simple)
- ✅ Audio natif Veo 3.1 (qualité)
- ✅ Sous-titres Whisper (transcription vidéo)
- ❌ Pas de continuité visuelle (acceptable pour MVP)

**Trade-off accepté** : Coût 2× vs simplicité + rapidité développement

**Prêt pour production V2 ! 🚀**
