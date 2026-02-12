# Flow de Synchronisation V2 - Veo 3.1 Fast

## Architecture Cloud Functions (Storage Triggers)

```
USER
  │
  ├─► [1] agent-script-v2 (HTTP)
  │    │
  │    ├─► Génère script BLOCS avec Gemini 2.5 Pro
  │    ├─► Sauvegarde gs://bucket/{video_id}/script_v2.json ✅
  │    └─► Update Firestore: v2_video_status → "script_generated"
  │
  │
[STORAGE TRIGGER] script_v2.json uploaded
  │
  └─► [2] agent-video-v2 (Cloud Event)
       │
       ├─► Génère BLOC 1 (8s) avec Veo 3.1 Fast
       ├─► Retourne operation_name (async)
       └─► Update Firestore: v2_veo_operations → "generating_block_1"
  
  
[CLOUD SCHEDULER] (toutes les minutes)
  │
  └─► [3] monitor-veo31 (HTTP)
       │
       ├─► Query Firestore: v2_veo_operations (status = processing)
       │
       ├─► Pour chaque operation:
       │    │
       │    ├─► Check operation.done()
       │    │
       │    ├─► Si DONE:
       │    │    │
       │    │    ├─► Download block_N.mp4 → gs://bucket/{video_id}/ ✅
       │    │    │
       │    │    ├─► Si block_N < total_blocks:
       │    │    │    │
       │    │    │    └─► Launch extension (BLOC N+1) avec prev_video
       │    │    │         │
       │    │    │         └─► Update Firestore → "generating_block_{N+1}"
       │    │    │
       │    │    └─► Si block_N == total_blocks:
       │    │         │
       │    │         ├─► Upload final block_N.mp4 ✅
       │    │         └─► Update Firestore → "ready_for_assembly"
       │    │
       │    └─► Si ERROR:
       │         │
       │         └─► Retry (3 max) ou mark as failed
       │
       └─► Return: {checked: X, processed: Y}


[STORAGE TRIGGER] block_N.mp4 uploaded (dernier bloc)
  │
  └─► [4] agent-assembler-v2 (Cloud Event)
       │
       ├─► Extrait audio de block_N.mp4
       ├─► Transcription Whisper
       ├─► Génère sous-titres ASS
       ├─► FFmpeg: add subs → final.mp4
       └─► Update Firestore → "completed"
```

## Détails des Triggers

### 1. agent-script-v2 → agent-video-v2

**Type:** Cloud Storage Trigger (automatique)  
**Événement:** `google.cloud.storage.object.v1.finalized`  
**Filter:** `*/script_v2.json`  
**Bucket:** `tiktok-pipeline-v2-artifacts`

**Flow:**
1. agent-script upload `{video_id}/script_v2.json`
2. Cloud Storage déclenche automatiquement agent-video-v2
3. CloudEvent contient: `{bucket: "...", name: "{video_id}/script_v2.json"}`
4. agent-video extrait `video_id` du path et charge le script

**Code:** [agent-video/main.py](agent-video/main.py#L18)
```python
@functions_framework.cloud_event
def generate_video_v2(cloudevent):
    data = cloudevent.data
    file_name = data["name"]  # {video_id}/script_v2.json
    video_id = file_name.split("/")[0]
```

---

### 2. monitor-veo31 → agent-assembler-v2

**Type:** Cloud Storage Trigger (automatique)  
**Événement:** `google.cloud.storage.object.v1.finalized`  
**Filter:** `*/block_*.mp4`  
**Bucket:** `tiktok-pipeline-v2-artifacts`

**Flow:**
1. monitor download final block et upload `{video_id}/block_N.mp4`
2. Cloud Storage déclenche automatiquement agent-assembler-v2
3. CloudEvent contient: `{bucket: "...", name: "{video_id}/block_N.mp4"}`
4. agent-assembler extrait `video_id` et traite la vidéo

**Code:** [agent-assembler/main.py](agent-assembler/main.py#L130)
```python
@functions_framework.cloud_event
def assemble_video(cloudevent):
    data = cloudevent.data
    file_name = data["name"]  # {video_id}/block_N.mp4
    video_id = file_name.split("/")[0]
```

---

## Cloud Scheduler

**Job:** `monitor-veo31-scheduler`  
**Schedule:** `* * * * *` (toutes les minutes)  
**URL:** `https://us-central1-{PROJECT_ID}.cloudfunctions.net/monitor-veo31`  
**Method:** POST  
**Headers:** `Content-Type: application/json`

---

## Firestore Collections

### v2_video_status

```json
{
  "video_id": "test_20260131_123456",
  "status": "script_generated | generating | assembling | completed | error",
  "blocks_count": 5,
  "duration": 36,
  "current_step": "script | video | assembly",
  "updated_at": "timestamp"
}
```

### v2_veo_operations

```json
{
  "video_id": "test_20260131_123456",
  "status": "generating_block_1 | generating_block_2 | ... | completed",
  "operation_name": "projects/.../operations/12345",
  "blocks": [
    {"block_num": 1, "status": "completed", "gcs_uri": "gs://..."},
    {"block_num": 2, "status": "processing", "operation_name": "..."}
  ],
  "current_block": 2,
  "total_blocks": 5,
  "retry_count": 0,
  "veo_version": "3.1-fast",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## Timeline d'une Génération

| Temps | Événement | Fonction | Firestore Status |
|-------|-----------|----------|------------------|
| T+0s  | User → POST script | agent-script-v2 | - |
| T+5s  | Script généré | agent-script-v2 | script_generated |
| T+6s  | Auto-trigger video | agent-script-v2 | - |
| T+7s  | Veo BLOC 1 lancé | agent-video-v2 | generating_block_1 |
| T+60s | Monitor check #1 | monitor-veo31 | generating_block_1 (en cours) |
| T+120s | BLOC 1 done | monitor-veo31 | generating_block_2 (extension lancée) |
| T+180s | Monitor check #2 | monitor-veo31 | generating_block_2 (en cours) |
| T+240s | BLOC 2 done | monitor-veo31 | generating_block_3 (extension lancée) |
| ... | ... | ... | ... |
| T+X | Dernier bloc done | monitor-veo31 | ready_for_assembly |
| T+X+1s | Auto-trigger assembly | monitor-veo31 | assembling |
| T+X+30s | Assembly terminé | agent-assembler-v2 | completed |

---

## Variables d'Environnement Requises

### agent-script-v2
- `GCP_PROJECT`: ID du projet GCP
- `BUCKET_NAME`: Bucket V2 (tiktok-pipeline-v2-artifacts)
- `AGENT_VIDEO_URL`: URL agent-video-v2

### agent-video-v2
- `GCP_PROJECT`: ID du projet GCP
- `BUCKET_NAME`: Bucket V2

### monitor-veo31
- `GCP_PROJECT`: ID du projet GCP
- `BUCKET_NAME`: Bucket V2
- `AGENT_ASSEMBLER_URL`: URL agent-assembler-v2

### agent-assembler-v2
- `GCP_PROJECT`: ID du projet GCP
- `BUCKET_NAME_V2`: Bucket V2

---

## Tests

### Test complet depuis local
```bash
# 1. Déployer les fonctions
bash deploy-functions-v2.sh

# 2. Lancer test
python test_flow_real_v2.py --theme "Intelligence Artificielle" --duration 15

# 3. Suivre logs
gcloud functions logs read monitor-veo31 --region=us-central1 --limit=50
```

### Test manuel des appels
```bash
# Script
curl -X POST https://us-central1-{PROJECT_ID}.cloudfunctions.net/agent-script-v2 \
  -H "Content-Type: application/json" \
  -d '{"theme": "Test", "video_id": "test_123", "target_duration": 15}'

# Video
curl -X POST https://us-central1-{PROJECT_ID}.cloudfunctions.net/agent-video-v2 \
  -H "Content-Type: application/json" \
  -d '{"video_id": "test_123"}'

# Monitor (déclenché par Cloud Scheduler)
curl -X POST https://us-central1-{PROJECT_ID}.cloudfunctions.net/monitor-veo31

# Assembler (déclenché par monitor)
curl -X POST https://us-central1-{PROJECT_ID}.cloudfunctions.net/agent-assembler-v2 \
  -H "Content-Type: application/json" \
  -d '{"video_id": "test_123"}'
```

---

## Points Clés

✅ **Storage triggers automatiques (comme V1)**  
✅ **Upload script_v2.json → Déclenche agent-video automatiquement**  
✅ **Upload block_N.mp4 → Déclenche agent-assembler automatiquement**  
✅ **monitor-veo31 géré par Cloud Scheduler (toutes les minutes)**  
✅ **Extensions Veo auto-combine les vidéos** (pas de concat manuel)  
✅ **Firestore synchronise l'état entre toutes les fonctions**  
✅ **Pas d'appels HTTP manuels** (sauf scheduler → monitor)  

---

## Prochaines Étapes

1. ✅ Déployer fonctions: `bash deploy-functions-v2.sh`
2. ✅ Tester flow: `python test_flow_real_v2.py`
3. ⏳ Intégrer backend: Appeler agent-script-v2 depuis API
4. ⏳ Intégrer frontend: UI sélection durée + monitoring
