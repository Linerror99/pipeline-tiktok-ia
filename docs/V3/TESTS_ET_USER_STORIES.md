# Reetik V3 — État de l'application, Tests & User Stories

> Mis à jour : 22 avril 2026  
> Branche : `v3_migration` · GCP project : `reetik-project` · DB Firestore : `reetik-v3`

---

## 1. Vue d'ensemble — Qu'est-ce que Reetik V3 ?

**Reetik** est un pipeline IA full-stack qui permet à un créateur TikTok de :
1. Créer un projet (thème, compte TikTok)
2. Définir des personnages récurrents via chat IA → image Imagen 4
3. Construire un scénario en dialoguant avec Gemini 3.1 Pro
4. Générer une vidéo 8–57s avec Veo 3.1 (audio natif, sans coupures)
5. Obtenir des suggestions TikTok IA (bio, hashtags, titres)

**Modèles IA utilisés :**

| Modèle | ID | Usage |
|--------|-----|-------|
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Chat personnages, scénarios, suggestions TikTok |
| Veo 3.1 GA | `veo-3.1-generate-001` | Génération vidéo 8s + extensions 7s |
| Veo 3.1 Fast | `veo-3.1-fast-generate-001` | Dev/tests moins chers |
| Imagen 4 | `imagen-4.0-generate-001` | Images personnages + thumbnails 9:16 |

---

## 2. Contenu de chaque dossier et son rôle

### `backend-v3/`
**FastAPI · Python 3.12 · Port 8080 (local: 8000)**  
Le cerveau de l'application. Gère l'auth, les projets, les personnages, scénarios, vidéos, et le TikTok.

```
backend-v3/
├── app/
│   ├── main.py              ← Point d'entrée FastAPI, CORS, routers
│   ├── config.py            ← Settings (buckets, JWT, CORS, Firestore "reetik-v3")
│   ├── models/
│   │   ├── auth.py          ← FirebaseLoginRequest, VerifyCodeRequest, UserResponse
│   │   ├── project.py       ← ProjectCreate, ProjectResponse
│   │   ├── character.py     ← CharacterChatRequest, CharacterResponse
│   │   ├── scenario.py      ← ScenarioChatRequest, ScenarioValidateRequest
│   │   └── video.py         ← VideoGenerateRequest, VideoStatusResponse, VALID_DURATIONS
│   ├── routers/
│   │   ├── auth.py          ← POST /verify-code, POST /login (Firebase), GET /me
│   │   ├── projects.py      ← CRUD /api/v3/projects/
│   │   ├── characters.py    ← Chat + génération Imagen 4
│   │   ├── scenarios.py     ← Chat + upload fichiers + validation
│   │   ├── videos.py        ← Lancer génération, statut, stream URL, download URL
│   │   ├── tiktok.py        ← Suggestions bio, hashtags, titres
│   │   └── websocket.py     ← WS /ws/v3/video/{id}?token= (progression live)
│   ├── services/
│   │   ├── firestore_service.py   ← Toutes les opérations Firestore (DB "reetik-v3")
│   │   ├── storage.py             ← Upload/download GCS (3 buckets V3)
│   │   ├── chat_service.py        ← Gemini 3.1 Pro (personnages + scénarios)
│   │   ├── character_service.py   ← Imagen 4 generation
│   │   ├── tiktok_service.py      ← Suggestions IA + parse JSON
│   │   └── notification_service.py ← Email SMTP quand vidéo terminée
│   └── utils/
│       ├── firebase.py      ← Firebase Admin init, Firestore client (DB reetik-v3)
│       └── jwt.py           ← create_access_token, get_current_user (dépendance)
├── Dockerfile               ← Multi-stage, expose 8080
└── requirements.txt         ← FastAPI, uvicorn, google-cloud-*, firebase-admin, PyJWT
```

**Docs Swagger disponibles sur :** `http://localhost:8000/api/v3/docs`

---

### `frontend-v3/`
**React 19 · Vite 7 · Tailwind 3.4 · Framer Motion 12 · Port 5173**  
Interface complète, dark theme (`#030014`), accents or (`#C9A96E`), inspirée ROX.com.

```
frontend-v3/src/
├── App.jsx                  ← Router (/, /login, /dashboard, /projects/:id)
├── main.jsx                 ← Point d'entrée React
├── config/
│   ├── api.js               ← Constantes API_BASE, WS_BASE, VALID_DURATIONS, VIDEO_STATUS
│   └── firebase.js          ← initializeApp Firebase, GoogleAuthProvider
├── contexts/
│   └── AuthContext.jsx      ← user, codeVerified, login(), logout(), verifyCode()
├── services/
│   ├── api.js               ← Instance Axios (Bearer token, interceptors)
│   ├── auth.js              ← loginWithGoogle(), verifyCode(), getMe(), logout()
│   ├── projects.js          ← list(), get(), create(), update(), remove()
│   ├── characters.js        ← list(), chat(), generate(), regenerate(), update()
│   ├── scenarios.js         ← list(), get(), chat(), upload(), validate()
│   ├── videos.js            ← list(), get(), generate(), getStatus(), connectWs()
│   └── tiktok.js            ← suggestProfile(), suggestHashtags(), suggestTitle()
├── pages/
│   ├── LandingPage.jsx      ← Hero + LogoBar + Features + HowItWorks + Stats + CTA
│   ├── LoginPage.jsx        ← Étape 1: Google Sign-In, Étape 2: code d'accès
│   ├── DashboardPage.jsx    ← Liste projets + création inline + suppression
│   └── ProjectPage.jsx      ← Tabs: Personnages / Scénario / Vidéos / TikTok
├── components/
│   ├── landing/
│   │   ├── Hero.jsx         ← Section hero avec CTA + animation
│   │   ├── LogoBar.jsx      ← Scroll infini des logos partenaires/technos
│   │   ├── Features.jsx     ← 6 features cards avec animations Framer Motion
│   │   ├── HowItWorks.jsx   ← 4 étapes numérotées
│   │   ├── Stats.jsx        ← Compteurs animés
│   │   └── CTA.jsx          ← Call to action final
│   ├── layout/
│   │   ├── Navbar.jsx       ← Sticky, blur on scroll, liens auth-aware
│   │   └── Footer.jsx       ← Liens + copyright
│   ├── project/
│   │   ├── ChatPanel.jsx    ← Composant chat réutilisable (messages + input)
│   │   ├── CharactersTab.jsx ← Chat IA + cards personnages + bouton Générer image
│   │   ├── ScenarioTab.jsx  ← Chat IA + upload fichier + durée + Valider
│   │   ├── VideosTab.jsx    ← Générer vidéo + progress WebSocket + liste vidéos
│   │   └── TikTokTab.jsx    ← Suggestions bio, hashtags, titres + copier
│   └── ui/
│       ├── Animations.jsx   ← RevealOnScroll, StaggerContainer, StaggerItem
│       ├── Buttons.jsx      ← GoldButton, SecondaryButton
│       └── Logo.jsx         ← Logo Reetik SVG
```

---

### `agent-video-veo31/`
**Cloud Function Gen2 · Python · Trigger HTTP**  
Génère la vidéo initiale 8s avec Veo 3.1, puis déclenche le monitor pour les extensions.

```
agent-video-veo31/
├── main.py          ← calculate_extensions(), snap_to_valid_duration(), build_prompt()
│                       Appel Veo API (8s initial) → écrit dans Firestore "reetik-v3"
└── requirements.txt
```

---

### `cloud-functions/monitor-extensions-v3/`
**Cloud Function Gen2 · Polling Firestore · Scheduler 30s**  
Surveille les opérations Veo en cours, lance les extensions 7s successives jusqu'à durée cible.

```
monitor-extensions-v3/
└── main.py  ← Firestore Client (DB "reetik-v3"), polling opération Veo, extension suivante
```

---

### `agent-thumbnail/`
**Cloud Function Gen2 · Imagen 4 · 9:16**  
Génère le thumbnail TikTok après chaque vidéo terminée. Format 768×1408.

```
agent-thumbnail/
└── main.py  ← Imagen 4, format 9:16, upload GCS bucket "reetik-v3-thumbnails"
```

---

### `terraform-v3/`
**Terraform · Infrastructure as Code complète**

```
terraform-v3/
├── main.tf        ← Provider Google Cloud, APIs requises
├── variables.tf   ← firestore_database_id="reetik-v3", region, buckets
├── firestore.tf   ← DB nommée "reetik-v3" + 6 index composites
├── storage.tf     ← 3 buckets (artifacts 90j, uploads 180j, thumbnails 365j) + CORS
├── functions.tf   ← 3 Cloud Functions (veo31, monitor, thumbnail) + var FIRESTORE_DATABASE
├── cloudrun.tf    ← Cloud Run backend-v3 (+ var FIRESTORE_DATABASE) · ⚠️ frontend manquant
├── scheduler.tf   ← Cloud Scheduler (polling 30s → monitor-extensions)
└── outputs.tf     ← URLs backend, functions, buckets
```

---

### `tests/`
**Pytest · Tests unitaires + intégration**

```
tests/
├── unit/
│   ├── test_backend_v3.py         ← ~35 tests (models, auth, projects, videos, tiktok, chat)
│   ├── test_veo31_extensions.py   ← ~25 tests calculs (extensions, durations, prompts)
│   └── test_agent_thumbnail.py    ← Tests agent thumbnail
└── integration/
    └── test_flow_v3.py            ← 5 scénarios end-to-end (flux complet mocké)
```

---

### `.github/workflows/`
```
deploy-v3.yml   ← 3 jobs : test (pytest) → deploy-backend (Cloud Run) → deploy-functions
```

---

### `docs/`
```
docs/
├── architecture-v3.drawio     ← Diagramme Draw.io complet (1920×1080, dark theme)
├── V3/
│   ├── TODO_V3.md             ← Plan original phase par phase
│   ├── V3_ARCHITECTURE.md     ← Architecture technique détaillée
│   └── V3_VEO31_EXTENSIONS.md ← Logique extensions Veo 3.1
└── plans/
    └── PLAN_DEVELOPPEMENT_COMPLET.md ← 10 phases, 17 améliorations
```

---

## 3. Ce qui est implémenté ✅

| Composant | Statut | Notes |
|-----------|--------|-------|
| Agent Veo 3.1 (extensions séquentielles) | ✅ Complet | 8s → jusqu'à 57s |
| Monitor extensions V3 | ✅ Complet | Polling 30s, Firestore DB isolée |
| Agent Thumbnail Imagen 4 | ✅ Complet | Format 9:16, bucket séparé |
| Backend V3 — Auth (Firebase + JWT) | ✅ Complet | Google Sign-In, code d'accès, JWT V3 |
| Backend V3 — Projets CRUD | ✅ Complet | Firestore "reetik-v3" |
| Backend V3 — Chat personnages (Gemini) | ✅ Complet | Historique, extraction traits |
| Backend V3 — Génération Imagen 4 | ✅ Complet | Upload GCS automatique |
| Backend V3 — Chat scénarios (Gemini) | ✅ Complet | Upload fichiers, validation |
| Backend V3 — Génération vidéo (Veo) | ✅ Complet | Lance agent, durées valides |
| Backend V3 — WebSocket suivi live | ✅ Complet | Progression % en temps réel |
| Backend V3 — Suggestions TikTok | ✅ Complet | Bio, hashtags, titres |
| Backend V3 — Notification email | ✅ Complet | SMTP, quand vidéo terminée |
| Terraform V3 — Infrastructure complète | ✅ Complet | DB, buckets, functions, scheduler |
| CI/CD GitHub Actions | ✅ Complet | test + deploy-backend + deploy-functions |
| Frontend V3 — Landing page | ✅ Complet | ROX.com-inspired, Framer Motion |
| Frontend V3 — Login (Google + code) | ✅ Complet | 2 étapes, AuthContext |
| Frontend V3 — Dashboard projets | ✅ Complet | Liste, création, suppression |
| Frontend V3 — Onglet Personnages | ✅ Complet | Chat + génération image |
| Frontend V3 — Onglet Scénario | ✅ Complet | Chat + upload + durée + valider |
| Frontend V3 — Onglet Vidéos | ✅ Complet | Générer + WebSocket live + liste |
| Frontend V3 — Onglet TikTok | ✅ Complet | Suggestions IA + copier |
| Tests unitaires backend | ✅ ~35 tests | Mocks Firebase/JWT |
| Tests unitaires Veo extensions | ✅ ~25 tests | Calculs purs, zéro API |
| Tests intégration flow complet | ✅ 5 scénarios | E2E mocké |
| Diagramme architecture Draw.io | ✅ Portfolio-ready | 1920×1080, dark |
| Firestore DB isolée "reetik-v3" | ✅ | Séparée de V2 "(default)" |

---

## 4. Ce qui reste à faire ⬜

| Priorité | Tâche | Détail |
|----------|-------|--------|
| 🔴 Deploy | `frontend-v3/Dockerfile` | Multi-stage Node → nginx:alpine |
| 🔴 Deploy | `frontend-v3/nginx.conf` | SPA routing (try_files → index.html) |
| 🔴 Deploy | `frontend-v3/.env.example` | VITE_API_URL, VITE_WS_URL, VITE_FIREBASE_* |
| 🔴 Deploy | `docker-compose.v3.yml` — service frontend | Port 3000:80, depends_on backend |
| 🔴 Deploy | `terraform-v3/cloudrun.tf` — resource frontend | Cloud Run ou Cloud Storage static |
| 🟡 Bug | `VideosTab.jsx` connectWs | callback ignoré, fonctionne mais incohérent |
| 🟡 Perf | Code splitting Vite | Bundle 570KB → lazy loading pages |
| 🟡 Test | Exécuter `pytest` pour valider | Jamais lancé sur ce poste |
| 🟡 Test | Lancer `npm run dev` et tester en vrai | Flow complet avec backend réel |
| 🟢 Futur | Templates style (7 styles visuels) | Phase 4 du plan |
| 🟢 Futur | Multi-langues (FR/EN/ES) | Phase 4 du plan |
| 🟢 Futur | Musique de fond | Phase 5 du plan |
| 🟢 Futur | Favoris & historique | Phase 6 du plan |
| 🟢 Futur | Cloud CDN + compression vidéo | Phase 7 du plan |
| 🟢 Futur | Tests E2E Playwright | Phase 8 du plan |
| 🟢 Futur | Cloud Monitoring dashboards | Phase 9 du plan |
| 🟢 Futur | Domaine custom + SSL prod | Phase 10 du plan |

---

## 5. Tests automatisés existants — Comment les lancer

```bash
# Depuis la racine du projet

# 1. Tests unitaires Veo 3.1 (zéro dépendance GCP, rapides)
pytest tests/unit/test_veo31_extensions.py -v

# 2. Tests unitaires Backend V3 (mocks Firebase)
cd backend-v3
pytest ../tests/unit/test_backend_v3.py -v

# 3. Tests intégration (flux complet mocké)
cd backend-v3
pytest ../tests/integration/test_flow_v3.py -v

# 4. Build frontend (valide les imports/exports)
cd frontend-v3
npm run build

# 5. Lint frontend
cd frontend-v3
npm run lint
```

---

## 6. User Stories & Tests fonctionnels manuels (Frontend)

> Prérequis : `backend-v3` lancé sur `http://localhost:8000`, `frontend-v3` lancé sur `http://localhost:5173`

---

### US-01 · Landing Page

**En tant que** visiteur, **je veux** voir une landing page attractive **pour** comprendre ce qu'est Reetik.

**Comment lancer :**
```bash
cd frontend-v3 && npm run dev
# Ouvrir http://localhost:5173
```

| # | Action | Résultat attendu |
|---|--------|-----------------|
| LND-01 | Ouvrir `http://localhost:5173` | Page noire (`#030014`), hero avec titre animé, bouton "Commencer" doré |
| LND-02 | Scroller vers le bas | Sections Features, HowItWorks, Stats, CTA apparaissent en reveal animé (Framer Motion) |
| LND-03 | Cliquer "Commencer" dans le hero | Redirige vers `/login` |
| LND-04 | LogoBar | Bande de logos qui défile en boucle infinie |
| LND-05 | Stats section | Compteurs animés (ex: "50 000 vidéos générées") |
| LND-06 | Navbar sticky | Reste visible en scrollant, fond flou au scroll |
| LND-07 | Redimensionner < 768px | Layout mobile responsive, pas d'overflow horizontal |

---

### US-02 · Authentification (Login en 2 étapes)

**En tant que** créateur invité, **je veux** me connecter avec Google + mon code d'accès **pour** accéder à l'app.

| # | Action | Résultat attendu |
|---|--------|-----------------|
| LOG-01 | Aller sur `/login` | Page sombre, logo Reetik, bouton "Continuer avec Google" |
| LOG-02 | Cliquer "Continuer avec Google" | Popup Google OAuth, choisir un compte |
| LOG-03 | Authentification Google réussie | Étape 2 : champ "Code d'accès" apparaît |
| LOG-04 | Entrer un code valide (ex: celui en Firestore) | Redirection vers `/dashboard` |
| LOG-05 | Entrer un code invalide | Message d'erreur rouge "Code invalide", pas de redirection |
| LOG-06 | Rafraîchir la page depuis `/dashboard` | Reste connecté (token en localStorage), pas de re-login |
| LOG-07 | Aller sur `/dashboard` sans être connecté | Redirigé vers `/login` |
| LOG-08 | Cliquer "Déconnexion" dans la navbar | Retour `/login`, localStorage vidé |

---

### US-03 · Dashboard — Gestion des projets

**En tant que** créateur, **je veux** voir, créer et supprimer mes projets TikTok.

| # | Action | Résultat attendu |
|---|--------|-----------------|
| DSH-01 | Arriver sur `/dashboard` | Salutation `Bonjour, {prénom}`, liste des projets (vide au départ) |
| DSH-02 | Cliquer "Nouveau projet" | Formulaire inline apparaît (Framer Motion) |
| DSH-03 | Remplir "Nom du projet" + "Thème" puis Submit | Redirection vers `/projects/{id}`, projet créé en Firestore |
| DSH-04 | Créer sans thème (thème optionnel) | Projet créé quand même |
| DSH-05 | Tenter de créer avec nom vide | Formulaire bloqué, bouton Créer désactivé |
| DSH-06 | Retourner au dashboard | Projet apparaît dans la liste avec compteurs |
| DSH-07 | Cliquer sur une card projet | Redirige vers `/projects/{id}` |
| DSH-08 | Cliquer icône poubelle sur un projet | Suppression avec confirmation visuelle, card disparaît |

---

### US-04 · Onglet Personnages — Chat IA + Génération Imagen 4

**En tant que** créateur, **je veux** définir mes personnages en conversant avec l'IA et générer leur image.

| # | Action | Résultat attendu |
|---|--------|-----------------|
| CHR-01 | Ouvrir un projet → onglet "Personnages" | Panel chat vide, compteur "0 personnages", placeholder explicatif |
| CHR-02 | Écrire "Je veux un personnage : une banane anime nommée Nano" | Message apparaît dans le chat, réponse IA en cours (spinner) |
| CHR-03 | IA répond avec questions de précision | Réponse affichée sous forme de bulle, style assistant |
| CHR-04 | Continuer la conversation jusqu'à extraction des traits | IA confirme les traits, une card personnage apparaît |
| CHR-05 | Card personnage visible | Nom, description, statut "draft", bouton "Générer image" |
| CHR-06 | Cliquer "Générer image" sur la card | Spinner sur le bouton, appel Imagen 4 (peut prendre 10–30s) |
| CHR-07 | Génération terminée | Image 9:16 affichée dans la card, bouton "Régénérer" disponible |
| CHR-08 | Cliquer "Régénérer" | Nouvelle image générée et remplace l'ancienne |
| CHR-09 | Rafraîchir la page | Personnages et images toujours présents (Firestore persistant) |
| CHR-10 | Créer 2 personnages différents | 2 cards indépendantes, chacune avec son image |

---

### US-05 · Onglet Scénario — Chat + Upload + Validation

**En tant que** créateur, **je veux** construire le scénario de ma vidéo en parlant à l'IA, puis le valider.

| # | Action | Résultat attendu |
|---|--------|-----------------|
| SCN-01 | Ouvrir onglet "Scénario" | Chat vide, durée par défaut 8s, bouton upload de fichier |
| SCN-02 | Écrire "Je veux faire une vidéo de 22s sur les bienfaits du café" | Réponse IA avec questions sur structure, ton, scènes |
| SCN-03 | Dialoguer jusqu'à obtenir un script complet | IA propose un script en blocs (VISUEL / DIALOGUE / SON) |
| SCN-04 | Sélectionner la durée "22s" dans le sélecteur | Durée mise à jour visuellement |
| SCN-05 | Uploader un fichier de référence (image/texte) | Fichier visible dans l'interface, pris en compte par l'IA |
| SCN-06 | Cliquer "Valider le scénario" | Statut passe à "validé", bouton désactivé ou remplacé |
| SCN-07 | Aller dans l'onglet Vidéos après validation | Bouton "Générer la vidéo" activé |
| SCN-08 | Essayer de valider sans scénario | Bouton désactivé ou erreur claire |

**Durées valides disponibles :** 8s · 15s · 22s · 29s · 36s · 43s · 50s · 57s

---

### US-06 · Onglet Vidéos — Génération + WebSocket + Lecture

**En tant que** créateur, **je veux** lancer la génération vidéo et suivre la progression en temps réel.

| # | Action | Résultat attendu |
|---|--------|-----------------|
| VID-01 | Ouvrir onglet "Vidéos" | Bouton "Générer la vidéo", liste vide si aucune vidéo |
| VID-02 | Cliquer "Générer la vidéo" | Spinner + message "Initialisation…", barre de progression 0% |
| VID-03 | Pendant la génération (8s) | Progression en temps réel via WebSocket (ex: "Génération clip initial… 25%") |
| VID-04 | Pour une vidéo 22s | Barre monte : 0% → 33% (clip 8s) → 66% (extension 1) → 100% |
| VID-05 | Génération terminée | Card vidéo apparaît avec statut "Terminée" (badge vert) |
| VID-06 | Cliquer "Lire" | Lecteur vidéo inline ou URL de streaming ouverte |
| VID-07 | Cliquer "Télécharger" | Téléchargement du fichier MP4 final |
| VID-08 | Fermer puis rouvrir l'onglet | Vidéo toujours listée, persistante |
| VID-09 | Erreur de génération | Message d'erreur rouge, barre de progression disparaît, retry possible |
| VID-10 | Rafraîchir pendant génération | WebSocket se reconnecte (ou statut affiché depuis Firestore) |

---

### US-07 · Onglet TikTok — Suggestions IA

**En tant que** créateur TikTok, **je veux** des suggestions IA de bio, hashtags et titres adaptés à mon projet.

| # | Action | Résultat attendu |
|---|--------|-----------------|
| TIK-01 | Ouvrir onglet "TikTok" | 3 sections : Profil / Hashtags / Titres, boutons "Générer" |
| TIK-02 | Cliquer "Générer profil" | Spinner, puis username (@...) + bio adaptés au thème du projet |
| TIK-03 | Cliquer "Générer hashtags" | Liste de hashtags (ex: #nano #banane #anime #tiktok) |
| TIK-04 | Cliquer "Générer titres" | 3 propositions de titres accrocheurs |
| TIK-05 | Cliquer le bouton copier sur un hashtag | Texte copié dans le presse-papier, feedback visuel "Copié !" |
| TIK-06 | Cliquer "Régénérer" | Nouvelles suggestions différentes |

---

### US-08 · Navigation & UX globale

| # | Action | Résultat attendu |
|---|--------|-----------------|
| NAV-01 | Utiliser les boutons Retour du navigateur | Navigation cohérente, pas de page blanche |
| NAV-02 | Accéder à `/projects/id_inconnu` | Redirigé vers `/dashboard` (try/catch loadProject) |
| NAV-03 | Charger dashboard avec backend éteint | Message d'erreur visible, pas de crash silencieux |
| NAV-04 | Tabs du projet (cliquer entre Personnages/Scénario/Vidéos/TikTok) | Animation Framer Motion (fade + slide), contenu correct |
| NAV-05 | Indicateur tab actif | Underline doré animé (`layoutId="tab-indicator"`) |
| NAV-06 | Responsive mobile (iPhone 14 Pro, 390px) | Pas de scroll horizontal, tabs scrollables horizontalement |

---

## 7. Ordre recommandé pour tester

```
Étape 1 — Tests automatisés (sans backend réel)
  pytest tests/unit/test_veo31_extensions.py -v   ← 100% isolé, doit passer à 100%
  pytest tests/unit/test_backend_v3.py -v          ← doit passer avec mocks

Étape 2 — Build frontend
  cd frontend-v3 && npm run build                  ← doit compiler sans erreur

Étape 3 — Lancer localement (avec credentials GCP)
  cd backend-v3
  GOOGLE_APPLICATION_CREDENTIALS=./credentials.json uvicorn app.main:app --reload --port 8000
  # Ouvrir http://localhost:8000/api/v3/docs → Swagger

  cd frontend-v3
  npm run dev
  # Ouvrir http://localhost:5173

Étape 4 — Flow manuel complet
  LND → LOG → DSH → CHR → SCN → VID → TIK
  (voir tableaux US-01 à US-08)

Étape 5 — Tests d'intégration (avec backend lancé)
  pytest tests/integration/test_flow_v3.py -v
```

---

## 8. Variables d'environnement nécessaires (local)

### Backend (`backend-v3/.env` ou variables système)
```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
JWT_SECRET_KEY=dev-secret-key-change-in-production-min-32-chars!!
PROJECT_ID=reetik-project
FIRESTORE_DATABASE=reetik-v3
BUCKET_NAME_V3=reetik-v3-artifacts
BUCKET_UPLOADS_V3=reetik-v3-uploads
BUCKET_THUMBNAILS_V3=reetik-v3-thumbnails
```

### Frontend (`frontend-v3/.env.local`)
```env
VITE_API_URL=http://localhost:8000/api/v3
VITE_WS_URL=ws://localhost:8000/ws/v3
VITE_FIREBASE_API_KEY=AIzaSyDSqTfHzJxUh9PZb3qZT5yKqJxN8gRJqFo
VITE_FIREBASE_AUTH_DOMAIN=pipeline-video-ia.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=pipeline-video-ia
VITE_FIREBASE_STORAGE_BUCKET=pipeline-video-ia.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=354616212471
VITE_FIREBASE_APP_ID=1:354616212471:web:abc123def456
```

> ⚠️ Les valeurs Firebase ci-dessus sont celles du fallback hardcodé dans `firebase.js`. Remplacer par les vraies valeurs si le projet Firebase change.

---

*Ce document est la référence de test pour le MVP V3. À mettre à jour après chaque session de test.*
