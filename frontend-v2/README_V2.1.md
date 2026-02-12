# Pipeline TikTok IA - Version 2.1

Version 2.1 avec frontend React TypeScript moderne et mises à jour en temps réel via WebSocket.

## 🎯 Nouveautés V2.1

### Backend
- ✅ **Firestore V2 Integration**: Status tracking via `v2_video_status` et `v2_veo_operations`
- ✅ **WebSocket Support**: Mises à jour en temps réel de la progression vidéo
- ✅ **Nouveaux Paramètres**: `target_duration` (8-78s), `style`, `language`
- ✅ **Storage V2**: Format d'URL standardisé `{video_id}/final.mp4`
- ✅ **Calcul de Progression**: Pourcentage basé sur status et blocs complétés

### Frontend
- ✅ **React 18.3 + TypeScript**: Type-safe et moderne
- ✅ **WebSocket Hook**: `useVideoProgress` avec reconnexion automatique
- ✅ **Pages Adaptées**:
  - CreateVideoPage: Formulaire avec durée, style, langue
  - GenerationProgressPage: Progression temps réel avec étapes
  - LibraryPage: Liste des vidéos avec status
  - VideoPlayerPage: Lecteur vidéo avec contrôles

## 📋 Prérequis

- Node.js 18+ (pour frontend)
- Python 3.12 (pour backend)
- Compte GCP avec projet `reetik-project`
- Cloud Functions V2 déployées

## 🚀 Installation Locale

### 1. Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Configurer variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs:
# - GCP_PROJECT_ID=reetik-project
# - BUCKET_NAME_V2=tiktok-pipeline-v2-artifacts-reetik-project
# - AGENT_SCRIPT_V2_URL=https://us-central1-reetik-project.cloudfunctions.net/agent-script-v2
# - ACCESS_CODE=dev-access-code-123
# - SECRET_KEY=your-jwt-secret-min-32-chars

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend-v2

# Installer dépendances
npm install

# Configurer variables d'environnement
# Copier .env.local déjà créé (pointe vers localhost:8000)

# Lancer le serveur de développement
npm run dev
```

## 🧪 Tests (Sans Génération Vidéo)

### Test Backend Uniquement

#### 1. Test Health Check
```bash
curl http://localhost:8000/
# Attendu: {"message": "Backend API v2.1.0", "status": "healthy"}
```

#### 2. Test Auth (Login fictif)
```bash
# Si vous avez un utilisateur dans Firestore
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass"
```

#### 3. Test Liste Vidéos
```bash
# Avec token JWT récupéré du login
curl http://localhost:8000/videos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Devrait retourner les vidéos existantes en Firestore
```

#### 4. Test Status Vidéo (avec video_id existant)
```bash
curl http://localhost:8000/videos/VIDEO_ID/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Frontend Uniquement

1. Ouvrir http://localhost:5173
2. Naviguer vers `/library` - doit charger les vidéos existantes
3. Cliquer sur une vidéo completed - doit afficher le lecteur
4. Vérifier les erreurs dans Console DevTools

### Test WebSocket (Sans Génération)

Dans la console DevTools du navigateur:
```javascript
// Remplacer VIDEO_ID et JWT_TOKEN
const ws = new WebSocket('ws://localhost:8000/ws/video/VIDEO_ID?token=JWT_TOKEN');

ws.onopen = () => console.log('WebSocket connected');
ws.onmessage = (event) => console.log('Message:', JSON.parse(event.data));
ws.onerror = (error) => console.error('WebSocket error:', error);

// Devrait recevoir des messages de status en temps réel
```

## 📊 Structure Firestore V2

### Collection: `v2_video_status`
```json
{
  "video_id": "test_video_123",
  "status": "script_generated" | "generating_parallel" | "ready_for_assembly" | "completed" | "failed",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z",
  "error_message": null,
  "final_url": "gs://bucket/test_video_123/final.mp4"
}
```

### Collection: `v2_veo_operations`
```json
{
  "video_id": "test_video_123",
  "theme": "Test theme",
  "total_blocks": 9,
  "completed_blocks": 9,
  "status": "completed",
  "operations": {
    "1": { "status": "completed", "operation_id": "op_123" },
    "2": { "status": "completed", "operation_id": "op_124" }
  },
  "clips_status": { "1": "uploaded", "2": "uploaded" },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z"
}
```

## 🔧 Backend API Endpoints

### Videos
- `POST /videos/create` - Créer une nouvelle vidéo
  ```json
  {
    "theme": "Les risques du sucre",
    "access_code": "dev-access-code-123",
    "target_duration": 36,
    "style": "informative",
    "language": "fr"
  }
  ```
  
- `GET /videos` - Lister toutes les vidéos
- `GET /videos/{video_id}/status` - Status d'une vidéo
- `GET /videos/{video_id}/download` - URL signée pour télécharger
- `GET /videos/{video_id}/stream` - URL signée pour streamer

### WebSocket
- `WS /ws/video/{video_id}?token={jwt}` - Connexion WebSocket pour updates temps réel

### Auth
- `POST /auth/login` - Login (form-data: username, password)
- `POST /auth/register` - Register
- `GET /auth/me` - User actuel

## 🎨 Frontend Pages

### CreateVideoPage (`/create`)
- Formulaire de création vidéo
- Paramètres: theme, duration (15/30/50/60s), style (4 choix), language (fr/en/es)
- Validation: theme requis
- Redirect vers `/progress/{video_id}` après création

### GenerationProgressPage (`/progress/:videoId`)
- WebSocket connection automatique
- Affiche progression en temps réel (0-100%)
- Étapes: Script → Scenes → Assembly → Complete
- Gère états: loading, processing, completed, failed
- Confetti animation à la completion

### LibraryPage (`/library`)
- Liste toutes les vidéos depuis API
- Filtrage par recherche
- Status badge (completed/processing/failed)
- Progress bar pour vidéos en cours
- Click → /video/{id} si completed, /progress/{id} si processing

### VideoPlayerPage (`/video/:videoId`)
- Lecteur vidéo avec contrôles
- Play/Pause, Mute, Fullscreen
- Download et Share buttons
- Métadonnées: theme, date, durée

## 📁 Structure Fichiers

```
backend/
├── app/
│   ├── main.py              # FastAPI app v2.1.0
│   ├── config.py            # BUCKET_NAME_V2
│   ├── routers/
│   │   ├── videos.py        # Endpoints vidéo
│   │   ├── websocket.py     # WebSocket router (NEW)
│   │   └── auth.py
│   └── services/
│       ├── video_generation.py  # Appel agent-script-v2
│       ├── storage.py           # Firestore V2 queries
│       └── firestore_service.py
├── requirements.txt         # + websockets, google-cloud-firestore
└── .env.example

frontend-v2/
├── src/
│   ├── config/
│   │   └── api.ts           # API & WS URLs (NEW)
│   ├── services/
│   │   └── api.ts           # API client avec ACCESS_CODE
│   ├── hooks/
│   │   └── useVideoProgress.ts  # WebSocket hook
│   ├── pages/
│   │   ├── CreateVideoPage.tsx      # ✅ Adapté
│   │   ├── GenerationProgressPage.tsx  # ✅ Adapté
│   │   ├── LibraryPage.tsx         # ✅ Adapté
│   │   └── VideoPlayerPage.tsx     # ✅ Adapté
│   └── components/
├── .env.local              # Dev config
├── .env.example
└── package.json
```

## 🐛 Debugging

### Backend Logs
```bash
# Lancer avec logs détaillés
uvicorn app.main:app --reload --log-level debug
```

### Frontend Console
- Ouvrir DevTools (F12)
- Onglet Console: Voir logs API et WebSocket
- Onglet Network: Voir requêtes HTTP
- Onglet WS: Voir messages WebSocket

### Firestore Debug
```bash
# Vérifier v2_video_status
gcloud firestore documents list v2_video_status --project=reetik-project

# Lire un document
gcloud firestore documents describe v2_video_status/VIDEO_ID --project=reetik-project
```

## 🚢 Déploiement (À FAIRE)

### Backend Cloud Run
```bash
cd backend
gcloud run deploy backend-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=reetik-project,BUCKET_NAME_V2=tiktok-pipeline-v2-artifacts-reetik-project
```

### Frontend Cloud Run
```bash
cd frontend-v2
# Build
npm run build

# Deploy (nécessite Dockerfile)
gcloud run deploy frontend-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars VITE_API_URL=https://backend-v2-xxx.run.app
```

## 📚 Documentation Complète

- [V2.1_MIGRATION.md](../V2.1_MIGRATION.md) - Guide de migration détaillé
- [MIGRATION_V2_RESUME.md](../MIGRATION_V2_RESUME.md) - Résumé V2 pipeline
- [FLOW_SYNC_V2.md](../FLOW_SYNC_V2.md) - Flow complet V2

## 🎯 Next Steps

1. ✅ Backend V2.1 adapté (Firestore, WebSocket)
2. ✅ Frontend pages adaptées
3. ⏳ Tests locaux sans génération vidéo
4. ⏳ Créer Dockerfiles pour Cloud Run
5. ⏳ Déployer sur Cloud Run
6. ⏳ Test end-to-end complet avec génération

---

**Version**: 2.1.0  
**Date**: February 2026  
**Status**: ✅ Backend Ready | ✅ Frontend Ready | ⏳ Testing
