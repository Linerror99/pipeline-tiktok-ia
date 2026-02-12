# Comparaison Architecture V1 vs V2

## V1 - Veo 3.0 (8 clips parallèles)

```
agent-script (HTTP)
    ↓ upload script.txt
    ↓
[STORAGE TRIGGER]
    ↓
agent-audio (Cloud Event)
    ↓ upload audio_1.mp3 ... audio_8.mp3
    ↓
[STORAGE TRIGGER]
    ↓
agent-video (Cloud Event)
    ↓ generate 8 clips parallèles via REST API
    ↓ upload video_clips/clip_1.mp4 ... clip_8.mp4
    ↓
[STORAGE TRIGGER]
    ↓
agent-assembler (Cloud Event)
    ↓ FFmpeg concat 8 clips
    ↓ Add TTS audio
    ↓ Whisper + sous-titres
    ↓ upload final.mp4
```

**Temps total:** ~5-10 minutes  
**Bucket:** `tiktok-pipeline-artifacts`  
**Firestore:** `video_status` simple  
**Triggers:** 3 Storage triggers  
**API:** Imagen REST API (synchrone)  

---

## V2 - Veo 3.1 Fast (extensions async)

```
agent-script-v2 (HTTP)
    ↓ upload script_v2.json
    ↓
[STORAGE TRIGGER]
    ↓
agent-video-v2 (Cloud Event)
    ↓ generate BLOC 1 (8s) avec Veo 3.1 SDK (async)
    ↓ retourne operation_name
    ↓ Firestore: v2_veo_operations
    ↓
[CLOUD SCHEDULER - 1 min]
    ↓
monitor-veo31 (HTTP)
    ↓ check operation.done()
    ↓ download block_1.mp4
    ↓ launch extension BLOC 2
    ↓ wait...
    ↓ download block_2.mp4
    ↓ launch extension BLOC 3
    ↓ ... jusqu'à block_N
    ↓ upload block_N.mp4
    ↓
[STORAGE TRIGGER]
    ↓
agent-assembler-v2 (Cloud Event)
    ↓ Extract audio (déjà inclus)
    ↓ Whisper + sous-titres
    ↓ upload final.mp4
```

**Temps total:** Variable (dépend nb blocs)  
**Bucket:** `tiktok-pipeline-v2-artifacts`  
**Firestore:** `v2_video_status` + `v2_veo_operations`  
**Triggers:** 2 Storage triggers + 1 HTTP scheduler  
**API:** Veo 3.1 SDK (async) + extensions  

---

## Différences Clés

| Aspect | V1 | V2 |
|--------|----|----|
| **Audio** | TTS séparé (agent-audio) | Audio natif Veo 3.1 |
| **Vidéo** | 8 clips parallèles (REST) | 1 bloc + extensions (SDK) |
| **Assemblage** | Concat 8 clips + TTS | Juste sous-titres |
| **Triggers** | 3 Storage triggers | 2 Storage + 1 Scheduler |
| **Pattern** | Synchrone (API REST) | Async (operations) |
| **Monitoring** | Aucun | monitor-veo31 |
| **Durée** | Fixe (~45s) | Variable (8-78s) |
| **Firestore** | Simple status | Operations tracking |
| **Retry** | Via Cloud Function retry | Via monitor custom retry |

---

## Migration Guide

### Fonctions à créer pour V2

1. ✅ **agent-script-v2** (modifier format BLOCS)
2. ❌ **agent-audio** (supprimer - audio natif)
3. ✅ **agent-video-v2** (Veo 3.1 SDK, async, Cloud Event)
4. ✅ **monitor-veo31** (NEW - monitoring async)
5. ✅ **agent-assembler-v2** (simplifier - audio + subs, Cloud Event)

### Cloud Storage Triggers

**V1:**
```bash
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=tiktok-pipeline-artifacts" \
--trigger-event-filters-path-pattern="attributes.name=script*.txt"
```

**V2:**
```bash
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=tiktok-pipeline-v2-artifacts" \
--trigger-event-filters-path-pattern="attributes.name=*/script_v2.json"
```

### Code Samples

**V1 - agent-audio (Cloud Event):**
```python
@functions_framework.cloud_event
def generate_audio(cloudevent):
    data = cloudevent.data
    bucket_name = data["bucket"]
    file_name = data["name"]  # script_xxx.txt
    
    if not file_name.startswith("script_"):
        return "OK"
```

**V2 - agent-video (Cloud Event):**
```python
@functions_framework.cloud_event
def generate_video_v2(cloudevent):
    data = cloudevent.data
    file_name = data["name"]  # {video_id}/script_v2.json
    
    if not file_name.endswith("/script_v2.json"):
        return "OK"
    
    video_id = file_name.split("/")[0]
```

---

## Avantages V2

✅ **Audio synchrone** (natif Veo, pas TTS séparé)  
✅ **Durée variable** (8-78s selon besoin)  
✅ **720p** (vs 480p V1)  
✅ **Moins d'agents** (4 vs 5)  
✅ **Retry intelligent** (monitor custom)  
✅ **Extensions auto-combine** (pas de concat FFmpeg complexe)  

## Inconvénients V2

⚠️ **Async** (plus complexe à monitorer)  
⚠️ **Temps variable** (dépend nb blocs)  
⚠️ **Coût** (Veo 3.1 plus cher que Veo 3.0)  
⚠️ **Dépendance Scheduler** (monitoring toutes les minutes)  

---

## Coexistence V1 / V2

- **V1:** main branch, bucket `tiktok-pipeline-artifacts`
- **V2:** v2_migration branch, bucket `tiktok-pipeline-v2-artifacts`
- **Backend:** Doit appeler agent-script-v2 pour V2
- **Frontend:** Doit permettre choix V1/V2 + durée

✅ Pas de conflit (buckets séparés, fonctions séparées)
