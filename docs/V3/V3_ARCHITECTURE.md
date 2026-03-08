# 🏗️ Reetik V3 - Architecture Complète

## Vision

Reetik V3 est une **plateforme de production TikTok** permettant de gérer des projets TikTok avec personnages récurrents, scénarios conversationnels, et vidéos Veo 3.1 continues (audio natif, pas de coupures).

**Stratégie** : 1 projet = 1 compte TikTok. Permet de tester plusieurs niches et de pivoter rapidement.

**Usage** : Personnel uniquement. V2.1 (reetik.ldjossou.com) reste intact pour le portfolio.

---

## 📦 Modèles IA V3

| Usage | Modèle | ID Vertex AI | Notes |
|-------|--------|-------------|-------|
| **Scripts / Chat IA** | Gemini 3.1 Pro | `gemini-3.1-pro-preview` | 1M tokens contexte, raisonnement avancé |
| **Génération Vidéo** | Veo 3.1 GA | `veo-3.1-generate-001` | Audio natif, extensions 7s, max 57s |
| **Génération Vidéo (Fast)** | Veo 3.1 Fast GA | `veo-3.1-fast-generate-001` | Plus rapide, pour tests dev |
| **Génération Personnages** | Imagen 4 | `imagen-4.0-generate-001` | Nano Banana, 9:16, jusqu'à 2816×1536 |
| **Voix Off (TTS)** | Gemini TTS | `gemini-2.5-pro-tts` | Voix Rasalgethi, inchangé |
| **Sous-titres** | Whisper | OpenAI Whisper | Transcription + sync ASS |

### Modèles Dépréciés (à supprimer avant le 2 avril 2026)

| Ancien (preview) | Nouveau (GA) |
|---|---|
| `veo-3.1-generate-preview` | `veo-3.1-generate-001` |
| `veo-3.1-fast-generate-preview` | `veo-3.1-fast-generate-001` |
| `veo-3.0-generate-preview` | `veo-3.0-generate-001` |
| `gemini-3-pro-preview` | `gemini-3.1-pro-preview` (suppression 26/03/2026) |

---

## 🏢 Structure du Projet

```
pipeline-tiktok-ia/
│
│  ── V2.1 (Portfolio - NE PAS TOUCHER) ──
├── backend/                  # Backend V2.1 (FastAPI) → reetik.ldjossou.com
├── frontend/                 # Frontend V2.1 (React) → reetik.ldjossou.com
├── terraform/                # Infra V2.1 (déployée)
│
│  ── V3 (Usage Perso - NOUVEAU) ──
├── backend-v3/               # Backend V3 (FastAPI) → NOUVEAU
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # FastAPI app V3
│       ├── config.py         # Config V3
│       ├── models/
│       │   ├── project.py    # Projets TikTok
│       │   ├── character.py  # Personnages Nano Banana
│       │   ├── scenario.py   # Scénarios vidéo
│       │   ├── video.py      # Vidéos V3
│       │   └── auth.py       # Auth Firebase
│       ├── routers/
│       │   ├── auth.py       # Firebase Auth Google
│       │   ├── projects.py   # CRUD projets
│       │   ├── characters.py # Chat IA + génération personnages
│       │   ├── scenarios.py  # Chat IA + validation scénarios
│       │   ├── videos.py     # Génération + download vidéos
│       │   ├── tiktok.py     # Helpers TikTok (hashtags, profil)
│       │   └── websocket.py  # WebSocket temps réel
│       ├── services/
│       │   ├── firestore_service.py
│       │   ├── storage.py
│       │   ├── video_generation.py
│       │   ├── chat_service.py       # Chat IA Gemini 3.1 Pro
│       │   ├── character_service.py  # Imagen 4 generation
│       │   ├── tiktok_service.py     # Suggestions TikTok
│       │   └── notification_service.py  # Email notifications
│       └── utils/
│
├── frontend-v3/              # Frontend V3 (React) → NOUVEAU
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx           # Firebase Auth Google
│   │   │   ├── Dashboard.jsx       # Liste projets
│   │   │   ├── ProjectCreate.jsx   # Création projet
│   │   │   ├── ProjectDetail.jsx   # Vue projet
│   │   │   ├── CharacterChat.jsx   # Chat IA personnages
│   │   │   ├── CharacterGallery.jsx # Galerie personnages
│   │   │   ├── ScenarioChat.jsx    # Chat IA scénarios
│   │   │   ├── VideoGeneration.jsx # Suivi génération
│   │   │   └── VideoLibrary.jsx    # Bibliothèque vidéos
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx   # Composant chat réutilisable
│   │   │   ├── FileUploader.jsx    # Upload fichiers/images
│   │   │   └── VideoPlayer.jsx     # Lecteur vidéo + thumbnail
│   │   └── services/
│   │       ├── api.js              # API backend-v3
│   │       └── firebase.js         # Firebase Auth config
│   └── ...
│
├── terraform-v3/             # Infra V3 séparée → NOUVEAU
│   ├── main.tf
│   ├── variables.tf
│   ├── cloud-run.tf          # backend-v3 + frontend-v3
│   ├── cloud-functions.tf    # Agents V3
│   ├── firestore.tf          # Collections V3
│   ├── storage.tf            # Buckets V3
│   ├── monitoring.tf         # Dashboards + Alertes
│   └── terraform.tfvars
│
│  ── Agents Cloud Functions ──
├── agent-script/             # Gemini 3.1 Pro scripts (partagé V2/V3)
├── agent-audio/              # TTS audio (partagé V2/V3)
├── agent-video/              # ANCIEN : 8 clips parallèles (V2.1 uniquement)
├── agent-video-veo31/        # NOUVEAU : Extensions Veo 3.1 continues
├── agent-assembler/          # FFmpeg + Whisper (simplifié pour V3 : 1 vidéo)
├── agent-chat/               # NOUVEAU : Chat IA conversationnel (Gemini 3.1 Pro)
├── agent-thumbnail/          # NOUVEAU : Landing pages TikTok (Imagen 4)
│
│  ── Tests Modulaires ──
├── tests/
│   ├── unit/
│   │   ├── test_veo31_extensions.py
│   │   ├── test_agent_script.py
│   │   ├── test_agent_chat.py
│   │   ├── test_agent_thumbnail.py
│   │   └── test_character_generation.py
│   ├── integration/
│   │   ├── test_full_pipeline_v3.py
│   │   └── test_firestore_v3.py
│   └── e2e/
│       └── test_frontend_v3.py
│
└── docs/
    └── V3/
        ├── V3_ARCHITECTURE.md        # Ce fichier
        ├── V3_VEO31_EXTENSIONS.md    # Fix Veo 3.1 extensions
        └── TODO_V3.md                # Sprint plan V3
```

---

## 🗄️ Firestore Collections V3

### `projects`
```json
{
  "project_id": "proj_abc123",
  "user_id": "firebase_uid",
  "name": "Mon Projet Foot",
  "description": "Compte TikTok dédié au football",
  "theme": "foot",
  "tiktok_account_info": {
    "username": "@football_facts",
    "bio_suggestion": "Les meilleurs moments du foot ⚽",
    "niche": "sport/football",
    "target_audience": "18-35 passionnés foot"
  },
  "main_character_id": "char_xyz",
  "secondary_character_ids": ["char_abc"],
  "video_count": 0,
  "status": "active",
  "created_at": "2026-03-08T...",
  "updated_at": "2026-03-08T..."
}
```

### `characters`
```json
{
  "character_id": "char_xyz",
  "project_id": "proj_abc123",
  "name": "Coach Max",
  "description": "Un entraîneur passionné, toujours en survêtement bleu",
  "personality_traits": ["passionné", "dynamique", "humour"],
  "visual_description": "Homme 35 ans, survêtement bleu, sifflet autour du cou",
  "catchphrases": ["Et BAM !", "Allez on y va !"],
  "image_url": "gs://v3-bucket/characters/char_xyz.png",
  "reference_images": [
    "gs://v3-bucket/characters/char_xyz_front.png",
    "gs://v3-bucket/characters/char_xyz_side.png"
  ],
  "is_main": true,
  "chat_history": [
    {"role": "user", "content": "Je veux un personnage coach sportif..."},
    {"role": "assistant", "content": "Super ! Quelques questions..."}
  ],
  "status": "validated",
  "created_at": "2026-03-08T..."
}
```

### `scenarios`
```json
{
  "scenario_id": "scen_123",
  "project_id": "proj_abc123",
  "title": "Top 5 buts de la semaine",
  "user_prompt": "Je veux une vidéo sur les meilleurs buts de cette semaine",
  "chat_history": [
    {"role": "user", "content": "Fais-moi une vidéo sur les buts de la semaine"},
    {"role": "assistant", "content": "Quelle durée tu veux ? Quel ton ?"},
    {"role": "user", "content": "22 secondes, ton dynamique"},
    {"role": "assistant", "content": "Voici le scénario..."}
  ],
  "uploaded_files": [
    {"type": "image", "url": "gs://v3-uploads/scen_123/ref1.jpg", "description": "Image de référence but"},
    {"type": "document", "url": "gs://v3-uploads/scen_123/stats.pdf", "description": "Stats semaine"}
  ],
  "final_script": {
    "blocks": [
      {"bloc": 1, "duration": 8, "dialogue": "...", "visuel": "..."},
      {"bloc": 2, "duration": 7, "dialogue": "...", "visuel": "..."},
      {"bloc": 3, "duration": 7, "dialogue": "...", "visuel": "..."}
    ],
    "total_duration": 22,
    "character_ids": ["char_xyz"]
  },
  "hashtags": ["#foot", "#buts", "#ligue1", "#topbuts", "#football"],
  "tiktok_title": "🔥 Top 5 BUTS de la semaine ! Tu devines le #1 ? 👀",
  "target_duration": 22,
  "status": "validated",
  "created_at": "2026-03-08T..."
}
```

### `videos_v3`
```json
{
  "video_id": "vid_v3_abc",
  "project_id": "proj_abc123",
  "scenario_id": "scen_123",
  "character_ids": ["char_xyz"],
  "video_url": "gs://v3-videos/vid_v3_abc/final.mp4",
  "thumbnail_url": "gs://v3-videos/vid_v3_abc/thumbnail.png",
  "duration": 22,
  "extensions_count": 2,
  "veo_model": "veo-3.1-generate-001",
  "has_native_audio": true,
  "hashtags": ["#foot", "#buts"],
  "tiktok_title": "🔥 Top 5 BUTS...",
  "download_count": 0,
  "status": "completed",
  "generation_started_at": "2026-03-08T...",
  "generation_completed_at": "2026-03-08T...",
  "notification_sent": true,
  "created_at": "2026-03-08T..."
}
```

---

## 📡 API Endpoints V3

### Auth (Firebase Google)
```
POST   /api/v3/auth/login          # Login Firebase token → JWT V3
GET    /api/v3/auth/me              # User info
POST   /api/v3/auth/verify-code    # Vérifier code accès (post-login)
```

### Projets
```
POST   /api/v3/projects/            # Créer projet TikTok
GET    /api/v3/projects/            # Lister mes projets
GET    /api/v3/projects/{id}        # Détail projet
PATCH  /api/v3/projects/{id}        # Modifier projet
DELETE /api/v3/projects/{id}        # Supprimer projet
```

### Personnages
```
POST   /api/v3/characters/chat              # Chat IA pour définir caractéristiques
POST   /api/v3/characters/generate          # Générer avec Imagen 4 (Nano Banana)
GET    /api/v3/characters/?project_id=...   # Lister personnages du projet
GET    /api/v3/characters/{id}              # Détail personnage
PATCH  /api/v3/characters/{id}              # Modifier personnage
DELETE /api/v3/characters/{id}              # Supprimer personnage
POST   /api/v3/characters/{id}/regenerate   # Re-générer image Imagen 4
```

### Scénarios
```
POST   /api/v3/scenarios/chat               # Chat IA pour scénario
POST   /api/v3/scenarios/upload             # Upload fichiers/images pour contexte
POST   /api/v3/scenarios/validate           # Valider scénario → prêt pour génération
GET    /api/v3/scenarios/?project_id=...    # Lister scénarios du projet
GET    /api/v3/scenarios/{id}               # Détail scénario
PATCH  /api/v3/scenarios/{id}               # Modifier scénario
DELETE /api/v3/scenarios/{id}               # Supprimer scénario
```

### Vidéos
```
POST   /api/v3/videos/generate              # Lancer génération (depuis scénario validé)
GET    /api/v3/videos/?project_id=...       # Lister vidéos du projet
GET    /api/v3/videos/{id}                  # Détail vidéo + statut
GET    /api/v3/videos/{id}/download         # URL signée pour download
GET    /api/v3/videos/{id}/status           # Statut génération (polling)
```

### Helpers TikTok
```
POST   /api/v3/tiktok/suggest-profile       # Suggestions profil TikTok
POST   /api/v3/tiktok/suggest-hashtags      # Hashtags intelligents par thème
POST   /api/v3/tiktok/suggest-title         # Titres accrocheurs
POST   /api/v3/tiktok/suggest-schedule      # Meilleurs horaires publication
```

### WebSocket
```
WS     /api/v3/ws/{video_id}               # Suivi temps réel génération
```

---

## 🔧 Logs Centralisés (Cloud Logging)

### Approche

Tous les services Cloud Run et Cloud Functions envoient automatiquement leurs logs vers Google Cloud Logging. On utilise **uniquement** le Log Explorer avec une vue sauvegardée — pas de page custom dans l'app.

### Filtre Log Explorer (Vue Sauvegardée)

```
resource.type IN ("cloud_run_revision", "cloud_function")
  AND (
    resource.labels.service_name =~ "backend-v3|agent-script|agent-video-veo31|agent-assembler|agent-chat|agent-thumbnail"
  )
```

→ Bookmark cette URL dans le navigateur pour accès 1 clic.

### Logs Structurés

Chaque module V3 utilise `print()` avec des préfixes clairs pour faciliter le filtrage :
```
🎬 [agent-video-veo31] Vidéo initiale 8s lancée pour vid_v3_abc
🔄 [agent-video-veo31] Extension 2/3 lancée pour vid_v3_abc
✅ [agent-video-veo31] Vidéo 22s complète pour vid_v3_abc
❌ [agent-video-veo31] Extension échouée: timeout
💬 [agent-chat] Chat personnage - 3 messages pour proj_abc123
🖼️ [agent-thumbnail] Imagen 4 généré pour char_xyz
📧 [backend-v3] Notification email envoyée pour vid_v3_abc
```

---

## 🔒 Authentification V3

### Firebase Auth (Google Sign-In)

```
Utilisateur → Google Sign-In → Firebase Auth → ID Token
                                                   ↓
                                         backend-v3 vérifie token
                                                   ↓
                                         JWT V3 interne (7 jours)
                                                   ↓
                                         Code d'accès requis
                                         pour utiliser l'app
```

### Flow

1. **Login** : Utilisateur se connecte via Google (Firebase Auth)
2. **Vérification** : Backend vérifie l'ID token Firebase
3. **Code d'accès** : Après login, l'utilisateur entre un code pour activer l'app
4. **JWT interne** : Backend émet un JWT V3 pour les requêtes suivantes
5. **Usage** : Toutes les requêtes API V3 nécessitent le JWT

### Pourquoi le code reste ?

> L'appli est à usage personnel. Le code d'accès post-login empêche tout accès non autorisé même si quelqu'un a ton Google account sur un autre appareil.

---

## 🎬 Durées Vidéo V3

### Paliers Disponibles (Veo 3.1 Extensions)

| Palier | Formule | Audio |
|--------|---------|-------|
| **8s** | 1 génération initiale | ✅ Natif continu |
| **15s** | 8s + 1 extension de 7s | ✅ Natif continu |
| **22s** | 8s + 2 extensions de 7s | ✅ Natif continu |
| **29s** | 8s + 3 extensions de 7s | ✅ Natif continu |
| **36s** | 8s + 4 extensions de 7s | ✅ Natif continu |
| **43s** | 8s + 5 extensions de 7s | ✅ Natif continu |
| **50s** | 8s + 6 extensions de 7s | ✅ Natif continu |
| **57s** | 8s + 7 extensions de 7s (MAX) | ✅ Natif continu |

### Durées de Test Dev

Pour économiser les tokens : **8s, 15s, 22s** uniquement.

### Pourquoi pas 180s ?

Veo 3.1 limite à 57s en continu (8s + 7×7s). Au-delà, il faudrait assembler plusieurs segments = même problème de coupures audio qu'en V2. On reste honnête avec l'utilisateur.

---

## 🔄 Séparation V2.1 / V3

### Principe

| | V2.1 (Portfolio) | V3 (Usage Perso) |
|---|---|---|
| **URL** | reetik.ldjossou.com | v3.reetik.ldjossou.com (ou autre) |
| **Backend** | `backend/` → Cloud Run | `backend-v3/` → Cloud Run V3 |
| **Frontend** | `frontend/` → Cloud Run | `frontend-v3/` → Cloud Run V3 |
| **Terraform** | `terraform/` (existant) | `terraform-v3/` (nouveau) |
| **Firestore** | Collections V2 | Collections V3 (prefix v3_) |
| **Storage** | Bucket V2 existant | Bucket V3 nouveau |
| **Auth** | JWT + code rotatif | Firebase Google + code post-login |
| **Modèle vidéo** | agent-video (8 clips) | agent-video-veo31 (extensions) |

### Règle d'or

> **On ne touche JAMAIS** au backend/, frontend/, terraform/. Ces dossiers servent le portfolio déployé. Toute modification V3 se fait dans les dossiers *-v3/.

---

## 📊 Flux Utilisateur V3 Complet

```
1. LOGIN
   └── Google Sign-In → Code d'accès → Dashboard

2. CRÉER UN PROJET
   └── Nom + Thème (foot/manga/food/...) + Description
   └── IA suggère : infos profil TikTok, bio, stratégie

3. CRÉER PERSONNAGE(S)
   └── Chat IA : discussion caractéristiques
   │   "Je veux un coach sportif dynamique..."
   │   → IA pose questions (apparence, personnalité, catchphrases)
   │   → Utilisateur valide
   └── Génération Imagen 4 : image de référence
   └── Personnage principal + secondaires (optionnel)

4. CRÉER UN SCÉNARIO VIDÉO
   └── Chat IA : discussion du contenu
   │   "Fais une vidéo sur les meilleurs buts..."
   │   → Upload fichiers/images de référence (optionnel)
   │   → IA lit les fichiers, comprend le contexte
   │   → IA propose script + durée + ton
   │   → Utilisateur modifie ou valide
   └── IA génère : hashtags + titre TikTok
   └── Utilisateur valide le scénario final

5. GÉNÉRER LA VIDÉO
   └── Veo 3.1 : vidéo initiale 8s + N extensions de 7s
   │   → Audio natif continu (pas de coupures)
   │   → Personnages référencés via character_references
   └── Imagen 4 : thumbnail/landing page TikTok
   └── Notification email quand terminé
   └── Suivi temps réel via WebSocket

6. TÉLÉCHARGER & PUBLIER
   └── Download vidéo MP4
   └── Download thumbnail
   └── Copier hashtags + titre
   └── Poster sur TikTok manuellement
```

---

## 🚀 Prochaines Étapes

Voir [TODO_V3.md](TODO_V3.md) pour le plan d'exécution par phases.
