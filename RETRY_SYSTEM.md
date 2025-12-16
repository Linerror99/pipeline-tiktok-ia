# 🔄 Système de Retry Automatique des Clips Vidéo

## Vue d'ensemble

Le système de retry automatique garantit que tous les clips vidéo sont générés même en cas d'échec temporaire de l'API Veo. Il se compose de 3 composants :

## Architecture

```
┌─────────────────┐
│  Agent Vidéo    │ ──┐
│  (Veo API)      │   │ Enregistre les opérations
└─────────────────┘   │ dans Firestore
                      ▼
              ┌────────────────┐
              │   Firestore    │
              │  video_ops     │ ◄─── Vérifie et met à jour
              └────────────────┘
                      ▲
                      │
┌─────────────────────┴───────┐
│  Cloud Function             │
│  check-and-retry-clips      │
│  (Toutes les 10 min)        │
└─────────────────────────────┘
                      │
                      │ Relance les clips
                      │ qui ont échoué
                      ▼
              ┌────────────────┐
              │  Veo API       │
              └────────────────┘
```

## Composants

### 1. Agent Vidéo (agent-video/main.py)

**Rôle** : Lancer les générations Veo et tracker les opérations

**Modifications** :
- Import de Firestore
- Fonction `save_operation_to_firestore()` pour enregistrer chaque opération
- Enregistrement du statut (`pending`, `failed`) après chaque appel API

**Document Firestore créé** :
```json
{
  "video_id": "theme_123456",
  "scene_index": 5,
  "operation_name": "projects/xxx/locations/us-central1/operations/12345",
  "prompt": "Cinematic, photorealistic...",
  "status": "pending",  // pending, success, failed, abandoned
  "created_at": "2025-11-09T15:30:00Z",
  "updated_at": "2025-11-09T15:30:00Z",
  "retry_count": 0
}
```

### 2. Cloud Function de Retry (check-and-retry-clips)

**Rôle** : Vérifier périodiquement les opérations et relancer celles qui ont échoué

**Déclenchement** : Cloud Scheduler toutes les 10 minutes

**Logique** :

1. **Récupérer les opérations `pending`** :
   - Filtre : `status == 'pending'` ET `updated_at < 15 minutes ago`
   - Ces opérations sont probablement bloquées ou ont échoué silencieusement

2. **Vérifier leur statut via l'API Veo** :
   - `GET /v1/{operation_name}` pour vérifier si l'opération est terminée
   - Si `done: true` → Mettre à jour `status = 'success'`
   - Si `error` → Relancer la génération

3. **Récupérer les opérations `failed`** :
   - Filtre : `status == 'failed'` ET `retry_count < 3`
   - Relancer automatiquement

4. **Relancer avec retry** :
   - Appeler l'API Veo avec le même prompt
   - Incrémenter `retry_count`
   - Mettre à jour `operation_name` et `status`

5. **Abandonner après 3 tentatives** :
   - Si `retry_count >= 3` → `status = 'abandoned'`
   - L'assembleur procédera avec les clips disponibles

### 3. Agent Assembleur (agent-assembler/main.py)

**Rôle** : Attendre un délai raisonnable puis assembler avec les clips disponibles

**Modifications** :

- Import de Firestore
- Création d'un document de tracking `assembly_tracking/{video_id}`
- Timeout de **20 minutes** avant assemblage forcé

**Logique** :

```python
if clips_manquants:
    if premiere_detection:
        # Créer le document de tracking
        # Attendre le prochain trigger
    else:
        if temps_ecoule < 20_minutes:
            # Continuer d'attendre
        else:
            # Assembler avec les clips disponibles
```

**Document Firestore créé** :
```json
{
  "video_id": "theme_123456",
  "expected_clips": 10,
  "found_clips": 9,
  "first_detected_at": "2025-11-09T15:30:00Z",
  "last_checked_at": "2025-11-09T15:45:00Z",
  "status": "waiting"  // waiting, timeout_assembly, completed
}
```

## Déploiement

### 1. Déployer l'agent vidéo mis à jour

```bash
cd agent-video
gcloud functions deploy generate-video-agent \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=generate_video \
    --trigger-bucket=tiktok-pipeline-artifacts-pipeline-video-ia \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="attributes.name=audio_*.mp3" \
    --timeout=540s \
    --memory=2Gi
```

### 2. Déployer l'agent assembleur mis à jour

```bash
cd agent-assembler
gcloud functions deploy assemble-video-agent \
    --gen2 \
    --runtime=python312 \
    --region=us-central1 \
    --source=. \
    --entry-point=assemble_video \
    --trigger-bucket=tiktok-pipeline-artifacts-pipeline-video-ia \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters-path-pattern="attributes.name=/video_clips/**/*.mp4" \
    --timeout=540s \
    --memory=4Gi
```

### 3. Déployer la Cloud Function de retry + Scheduler

```bash
cd cloud-functions
chmod +x deploy-retry-function.sh
./deploy-retry-function.sh
```

Ce script va :
- Déployer la Cloud Function `check-and-retry-clips`
- Créer un Cloud Scheduler job qui l'exécute toutes les 10 minutes

## Monitoring

### Vérifier les opérations en cours

```bash
# Logs de l'agent vidéo
gcloud functions logs read generate-video-agent --gen2 --region=us-central1 --limit=50

# Logs de la fonction de retry
gcloud functions logs read check-and-retry-clips --gen2 --region=us-central1 --limit=50

# Logs de l'assembleur
gcloud functions logs read assemble-video-agent --gen2 --region=us-central1 --limit=50
```

### Firestore Console

Accéder à Firestore pour voir les opérations :

```
https://console.cloud.google.com/firestore/data/video_operations
```

Collections :
- `video_operations` : Toutes les opérations de génération de clips
- `assembly_tracking` : Tracking de l'assemblage par vidéo

### Déclencher manuellement un retry

```bash
# Récupérer l'URL de la fonction
FUNCTION_URL=$(gcloud functions describe check-and-retry-clips \
    --gen2 --region=us-central1 --format='value(serviceConfig.uri)')

# Appeler la fonction
curl $FUNCTION_URL
```

## Scénarios

### Scénario 1 : Clip échoue immédiatement

1. Agent vidéo appelle Veo API → erreur 500
2. Agent vidéo enregistre `status = 'failed'` dans Firestore
3. Dans les 10 minutes, la fonction de retry relance
4. Si succès → `status = 'pending'`
5. Vérification dans 10 minutes → `status = 'success'`
6. Assembleur détecte tous les clips → assemble

### Scénario 2 : Clip bloqué (timeout)

1. Agent vidéo appelle Veo API → `operation_name` retourné
2. Agent vidéo enregistre `status = 'pending'`
3. Après 15 minutes, toujours pending
4. Fonction de retry vérifie l'opération via API
5. Si échec → relance automatiquement
6. Nouveau `operation_name` enregistré

### Scénario 3 : Clip ne revient jamais (3 échecs)

1. Premier échec → retry 1
2. Deuxième échec → retry 2
3. Troisième échec → retry 3
4. Après 3 échecs → `status = 'abandoned'`
5. Assembleur attend 20 minutes
6. Timeout atteint → assemble avec les clips disponibles

### Scénario 4 : Tous les clips réussissent

1. Agent vidéo lance 10 clips
2. Tous retournent `operation_name`
3. Veo génère les clips en 5-10 minutes
4. Fonction de retry vérifie → tous `status = 'success'`
5. Assembleur détecte 10/10 clips → assemble immédiatement

## Avantages

✅ **Robustesse** : Gère automatiquement les échecs temporaires de Veo
✅ **Efficacité** : Ne relance que les clips qui ont échoué
✅ **Visibilité** : Tracking complet dans Firestore
✅ **Pas de blocage** : L'assembleur finit par assembler même avec des clips manquants
✅ **Limite de retry** : 3 tentatives max pour éviter les boucles infinies

## Coûts

- **Cloud Scheduler** : ~$0.10/mois (1 job, 4,320 exécutions/mois)
- **Cloud Function retry** : ~$0.01/mois (très peu d'exécutions en pratique)
- **Firestore** : ~$0.06/mois (quelques documents par vidéo)

**Total** : ~$0.17/mois 🎉

## FAQ

**Q : Que se passe-t-il si un clip échoue 3 fois ?**
R : Il est marqué `abandoned` et l'assembleur continue avec les autres clips.

**Q : Combien de temps avant l'assemblage avec clips manquants ?**
R : 20 minutes après la première détection de clips.

**Q : Peut-on relancer manuellement un clip abandonné ?**
R : Oui, il suffit de mettre à jour `retry_count = 0` dans Firestore et la fonction relancera.

**Q : Les retries augmentent-ils les coûts Veo ?**
R : Oui, chaque retry est une nouvelle génération facturée (~$0.05-0.10/clip).
