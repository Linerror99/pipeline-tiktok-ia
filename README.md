# 🎬 Reetik - Génération Automatique de Vidéos IA

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Pro-orange)](https://deepmind.google/technologies/gemini/)
[![Veo](https://img.shields.io/badge/Veo-3.1-red)](https://deepmind.google/technologies/veo/)

Pipeline complète de génération automatique de vidéos TikTok/Shorts virales à partir d'un simple thème. Utilise Gemini 2.5 Pro, **Veo 3.1** (modèle vidéo IA le plus avancé), Google TTS Premium, et Whisper.

---

## 🚀 Fonctionnalités

- ✅ **Génération de script IA** avec Gemini 2.5 Pro
- ✅ **Voix off premium** (voix Gemini naturelle)
- ✅ **Clips vidéo créatifs** générés par **Veo 3.1** (qualité cinématique, mouvement fluide, cohérence temporelle)
- ✅ **Sous-titres style TikTok** synchronisés (Whisper + ASS)
- ✅ **Format optimisé** : 9:16, 64-80 secondes, HD 1080p
- ✅ **Pipeline entièrement automatisée** : 1 requête → vidéo complète en ~6-10 minutes

---

## 📊 Architecture

### Architecture Globale

```
Utilisateur → Frontend (React/Cloud Run) → Backend API (FastAPI/Cloud Run) → Cloud Functions → Vertex AI (Gemini + Veo)
                                              ↓
                                        Cloud Storage
                                              ↓
                                     Vidéo Finale (MP4)
```

### Pipeline de Génération

```
Thème → Agent Script (Gemini) → Agent Audio (TTS) → Agent Vidéo (Veo) → Agent Assembleur (FFmpeg+Whisper) → Vidéo Finale
```

**Infrastructure** :
- **Frontend** : React + Vite déployé sur Cloud Run (interface web moderne)
- **Backend** : FastAPI déployé sur Cloud Run (API REST + WebSocket)
- **Cloud Functions** : 4 agents de génération + rotation code d'accès + monitoring
- **Stockage** : Cloud Storage avec CORS pour lecture vidéos
- **Base de données** : Firestore (utilisateurs, vidéos, quotas)
- **CI/CD** : GitHub Actions avec Workload Identity Federation

---

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | React 18 + TypeScript + Vite + TailwindCSS |
| **Backend** | FastAPI (Python 3.12) + Pydantic |
| **Script Generation** | Gemini 2.5 Pro |
| **Voix Off** | Google TTS Premium (Gemini voice) |
| **Génération Vidéo** | **Veo 3.1** (format 9:16, HD 1080p, qualité Pro) |
| **Sous-titres** | OpenAI Whisper + ASS format |
| **Assemblage** | FFmpeg |
| **Authentification** | JWT + Firestore |
| **Base de données** | Firestore (quotas, utilisateurs) |
| **Cloud Functions** | Python 3.12 Gen2 (agents + monitoring) |
| **Hosting** | Cloud Run (Backend + Frontend) |
| **Stockage** | Cloud Storage (vidéos + artifacts) |
| **Infrastructure** | Terraform + GitHub Actions |
| **CI/CD** | Workload Identity Federation |

---

## 📋 Prérequis

### Pour Utiliser l'Application
- **Navigateur web** moderne (Chrome, Firefox, Edge)
- **Code d'accès** (obtenu via la Cloud Function de rotation)

### Pour Développer/Déployer
- **Compte Google Cloud** avec facturation activée
- **Projet GCP** configuré (ex: reetik-project)
- **APIs activées** (automatisé via Terraform) :
  - Cloud Run API
  - Cloud Functions API
  - Cloud Storage API
  - Vertex AI API
  - Text-to-Speech API
  - Cloud Build API
  - Artifact Registry API
  - Firestore API
  - Secret Manager API
- **Outils installés** :
  - Terraform >= 1.0
  - gcloud CLI
  - Docker (pour développement local)
  - Git
- **GitHub** (pour CI/CD avec Actions)

---

## � Démarrage Rapide

### 🌐 Utiliser l'Application (Production)

1. **Accéder à l'interface web** : [Reetik Production](https://portfolio-prod-portfolio-app-588105049123.us-west1.run.app)

2. **Obtenir le code d'accès** :
   ```bash
   curl https://rotate-access-code-5ranhgrf2q-uc.a.run.app/
   ```
   Ou consultez Firestore : `config/access_code`

3. **S'inscrire** avec email, mot de passe et code d'accès

4. **Créer des vidéos** via l'interface web (quota: 2 vidéos/utilisateur)

### 🔧 Développement Local

#### Avec Docker Compose (Recommandé)

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/pipeline-tiktok-ia.git
cd pipeline-tiktok-ia

# 2. Configurer les credentials GCP
# Placer credentials.json dans backend/

# 3. Lancer l'environnement complet
docker-compose up

# Frontend : http://localhost:3000
# Backend API : http://localhost:8000
# Docs API : http://localhost:8000/docs
```

#### Configuration Manuelle

```bash
# Backend
cd backend
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS="credentials.json"
export GCP_PROJECT_ID="reetik-project"
uvicorn app.main:app --reload --port 8000

# Frontend (nouveau terminal)
cd frontend-v2
npm install
npm run dev
# http://localhost:5173
```

### 🏗️ Déploiement Production

#### Option 1 : CI/CD Automatique (Recommandé)

```bash
# 1. Configurer GitHub Secrets
# Dans Settings > Secrets and variables > Actions :
# - WIF_PROVIDER
# - WIF_SERVICE_ACCOUNT  
# - BACKEND_SECRET_KEY

# 2. Push vers main
git push origin main

# GitHub Actions déploie automatiquement :
# ✅ Build images Docker
# ✅ Push vers Artifact Registry
# ✅ Deploy Backend + Frontend sur Cloud Run
```

#### Option 2 : Terraform Manuel

```bash
# 1. Initialiser Terraform
cd terraform
terraform init

# 2. Configurer les variables
cp terraform.tfvars.example terraform.tfvars
# Éditer terraform.tfvars avec vos valeurs

# 3. Déployer l'infrastructure
terraform plan
terraform apply

# 4. Build et push des images Docker
cd ..
./scripts/build-and-push-prod.sh

# 5. Déployer sur Cloud Run
gcloud run deploy tiktok-backend \
  --image us-central1-docker.pkg.dev/reetik-project/tiktok-pipeline/backend:latest \
  --region us-central1

gcloud run deploy tiktok-frontend \
  --image us-central1-docker.pkg.dev/reetik-project/tiktok-pipeline/frontend:latest \
  --region us-central1
```

> 📖 **Guide complet** : Consultez [docs/deployment/PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md)

---

## 🎬 Utilisation

### Via l'Interface Web (Recommandé)

1. **Accéder à l'application** : https://portfolio-prod-portfolio-app-588105049123.us-west1.run.app

2. **S'authentifier** avec le code d'accès actuel

3. **Créer une vidéo** :
   - Entrer un thème viral (ex: "Les secrets de la pyramide de Khéops")
   - Cliquer sur "Générer la vidéo"
   - Suivre la progression en temps réel (WebSocket)
   - Télécharger ou visualiser la vidéo finale

### Exemples de Thèmes Viraux

- 🏛️ **Mystères historiques** : "Les pyramides de Bosnie - mythe ou réalité"
- 🔬 **Technologies anciennes** : "Les technologies impossibles des anciens Égyptiens"
- 🌊 **Phénomènes inexpliqués** : "Le triangle des Bermudes - nouvelle découverte 2024"
- 🗿 **Civilisations perdues** : "Les statues de l'Île de Pâques et leur secret"
- 🚀 **Mystères spatiaux** : "Les signaux radio mystérieux de l'espace profond"

### Via l'API (Pour développeurs)

```bash
# 1. S'authentifier
TOKEN=$(curl -X POST https://tiktok-backend-vrzs3y5aoq-uc.a.run.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass","access_code":"CODE"}' \
  | jq -r '.access_token')

# 2. Créer une vidéo
curl -X POST https://tiktok-backend-vrzs3y5aoq-uc.a.run.app/videos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme": "Les secrets cachés de la Grande Muraille de Chine"}'

# 3. Lister vos vidéos
curl -X GET https://tiktok-backend-vrzs3y5aoq-uc.a.run.app/videos/ \
  -H "Authorization: Bearer $TOKEN"
```

> 📖 **API Documentation** : https://tiktok-backend-vrzs3y5aoq-uc.a.run.app/docs

---

## 📊 Monitoring & Logs

### Interface Web (Temps Réel)

- **Suivi de progression** : WebSocket en temps réel dans l'interface
- **Historique des vidéos** : Page "Mes Vidéos" avec statuts
- **Notifications** : Alertes en temps réel via WebSocket

### Cloud Console (Administration)

#### Services Principaux
- **Backend Cloud Run** : https://console.cloud.google.com/run/detail/us-central1/tiktok-backend
- **Frontend Cloud Run** : https://console.cloud.google.com/run/detail/us-central1/tiktok-frontend
- **Cloud Functions** : https://console.cloud.google.com/functions/list
- **Storage** : https://console.cloud.google.com/storage/browser/tiktok-pipeline-v2-artifacts-reetik-project
- **Firestore** : https://console.firebase.google.com/project/reetik-project/firestore

#### Logs

```bash
# Logs Backend Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=tiktok-backend" \
  --limit=50 --format=json

# Logs Cloud Functions (Agent Assembleur)
gcloud functions logs read generate-assembler-agent-v2 \
  --gen2 --region=us-central1 --limit=50

# Logs Firestore
gcloud logging read "resource.type=cloud_firestore_database" \
  --limit=20
```

#### Métriques Cloud Run

```bash
# Requêtes Backend
gcloud monitoring time-series list \
  --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'

# Latence
gcloud monitoring time-series list \
  --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"'
```

> ⚠️ **Monitoring avancé** : Configuration en cours (voir section suivante)

---

## ⏱️ Durées de Traitement

| Étape | Durée |
|-------|-------|
| Script | 5-10 secondes |
| Audio | 20-30 secondes |
| Vidéo (8 clips en parallèle) | 3-5 minutes |
| Assemblage + Sous-titres | 2-3 minutes |
| **TOTAL** | **~6-10 minutes** |

---

## 💰 Coûts Estimés

### Par Vidéo Générée

| Service | Coût par Vidéo |
|---------|----------------|
| Gemini 2.5 Pro (script) | ~$0.02 |
| Google TTS Premium (audio) | ~$0.05 |
| **Veo 3.1** (8 clips x 8s, HD 1080p) | ~$6.40 |
| Cloud Functions (4 agents) | ~$0.10 |
| Cloud Storage (stockage) | ~$0.01 |
| **TOTAL** | **~$6.58** |

### Infrastructure Mensuelle (Idle)

| Service | Coût Mensuel |
|---------|-------------|
| Cloud Run Backend (0 min instances) | $0 (pay-per-use) |
| Cloud Run Frontend (0 min instances) | $0 (pay-per-use) |
| Cloud Functions (idle) | $0 (pay-per-invocation) |
| Firestore (petite base) | ~$1-2 |
| Cloud Storage (100 vidéos) | ~$2-3 |
| Cloud Scheduler (rotation code) | ~$0.10 |
| Artifact Registry | ~$0.10 |
| **TOTAL (sans générations)** | **~$3-5/mois** |

### Exemple : 20 vidéos/mois
- Infrastructure : ~$5
- 20 vidéos × $6.58 : ~$132
- **Total mensuel** : **~$137**

> 💡 **Optimisation** : Utilisez les quotas utilisateurs (2 vidéos/user) pour contrôler les coûts

---

## 🐛 Troubleshooting

### Problèmes d'Authentification

**Erreur : "Code d'accès invalide"**
```bash
# 1. Obtenir le code actuel (change toutes les heures)
curl https://rotate-access-code-5ranhgrf2q-uc.a.run.app/

# 2. Vérifier dans Firestore
# Console Firebase > Firestore > config/access_code
```

**Erreur : "Quota dépassé"**
- Vérifiez votre quota dans l'interface (max: 2 vidéos/utilisateur)
- Les admins (`is_admin: true` dans Firestore) ont un quota illimité

### Problèmes de Génération

**Vidéo bloquée en "processing"**
```bash
# Vérifier les logs de la Cloud Function concernée
gcloud functions logs read generate-assembler-agent-v2 --gen2 --region=us-central1 --limit=20

# Vérifier le statut dans Firestore
# Collection: videos > Document ID > status
```

**Clips dans le mauvais ordre**
- Le système de retry automatique corrige ce problème
- Vérifiez les logs : `gcloud functions logs read monitor-and-assemble`

**CORS error lors du chargement vidéo**
```bash
# Vérifier la configuration CORS du bucket
gsutil cors get gs://tiktok-pipeline-v2-artifacts-reetik-project

# Reconfigurer si nécessaire (voir terraform/storage.tf)
```

### Problèmes de Déploiement

**GitHub Actions échoue**
```bash
# Vérifier les secrets GitHub
# Settings > Secrets and variables > Actions
# Requis : WIF_PROVIDER, WIF_SERVICE_ACCOUNT, BACKEND_SECRET_KEY
```

**Cloud Run service ne démarre pas**
```bash
# Vérifier les logs de démarrage
gcloud run services logs read tiktok-backend --region=us-central1 --limit=50

# Vérifier les variables d'environnement
gcloud run services describe tiktok-backend --region=us-central1 --format=yaml
```

> 📖 **Troubleshooting détaillé** : Consultez [docs/deployment/](docs/deployment/)

---

## 📁 Structure du Projet

```
pipeline-tiktok-ia/
├── agent-script/           # Agent génération script (Gemini)
├── agent-audio/            # Agent génération audio (TTS)
├── agent-video/            # Agent génération vidéo (Veo)
├── agent-assembler/        # Agent assemblage (FFmpeg + Whisper)
├── backend/                # API FastAPI (Cloud Run)
├── frontend-v2/            # Application React + TypeScript (Cloud Run)
├── cloud-functions/        # Cloud Functions (rotation, monitoring)
├── terraform/              # Infrastructure as Code
├── scripts/                # Scripts de déploiement et utilitaires
├── docs/                   # Documentation organisée
│   ├── deployment/         # Guides de déploiement
│   ├── architecture/       # Architecture et systèmes
│   ├── migration/          # Historique des migrations
│   ├── plans/              # Plans et analyses
│   └── legacy/             # Documentation obsolète (référence)
├── docker-compose.yml      # Environnement local de développement
├── firestore.rules         # Règles de sécurité Firestore
└── README.md               # Ce fichier
```

---

## 📚 Documentation Détaillée

La documentation complète est organisée dans le dossier `docs/` :

### Déploiement (`docs/deployment/`)
- **[DEPLOYMENT_GUIDE.md](docs/deployment/DEPLOYMENT_GUIDE.md)** - Guide complet de déploiement
- **[PRODUCTION_DEPLOYMENT.md](docs/deployment/PRODUCTION_DEPLOYMENT.md)** - Déploiement production (Cloud Run + CI/CD)
- **[WIF_SETUP.md](docs/deployment/WIF_SETUP.md)** - Configuration Workload Identity Federation
- **[PRODUCTION_URLS.md](docs/deployment/PRODUCTION_URLS.md)** - URLs et endpoints de production
- **[SERVICE_ACCOUNT_SETUP.md](docs/deployment/SERVICE_ACCOUNT_SETUP.md)** - Configuration des service accounts
- **[DOCKER_OPTIMIZATION.md](docs/deployment/DOCKER_OPTIMIZATION.md)** - Optimisation des images Docker

### Architecture (`docs/architecture/`)
- **[AUTH_SYSTEM.md](docs/architecture/AUTH_SYSTEM.md)** - Système d'authentification complet
- **[ACCESS_CODE_SYSTEM.md](docs/architecture/ACCESS_CODE_SYSTEM.md)** - Système de codes d'accès rotatifs
- **[RETRY_SYSTEM.md](docs/architecture/RETRY_SYSTEM.md)** - Système de retry automatique
- **[FLOW_SYNC_V2.md](docs/architecture/FLOW_SYNC_V2.md)** - Flow de synchronisation V2
- **[Structure_actuelle.md](docs/architecture/Structure_actuelle.md)** - Structure actuelle détaillée

### Migration (`docs/migration/`)
- **[MIGRATION_V2_RESUME.md](docs/migration/MIGRATION_V2_RESUME.md)** - Résumé migration V2
- **[V1_VS_V2_COMPARISON.md](docs/migration/V1_VS_V2_COMPARISON.md)** - Comparaison V1 vs V2
- **[V2.1_MIGRATION.md](docs/migration/V2.1_MIGRATION.md)** - Migration V2.1

### Plans & Analyses (`docs/plans/`)
- **[PLAN_DEVELOPPEMENT_COMPLET.md](docs/plans/PLAN_DEVELOPPEMENT_COMPLET.md)** - Plan de développement complet
- **[PLAN_EVOLUTION_V2.md](docs/plans/PLAN_EVOLUTION_V2.md)** - Plan d'évolution V2
- **[EVOLUTION_VEO3.1.md](docs/plans/EVOLUTION_VEO3.1.md)** - Évolution vers Veo 3.1
- **[PRICING_ANALYSIS_REAL.md](docs/plans/PRICING_ANALYSIS_REAL.md)** - Analyse de coûts réels

---

## 🔒 Sécurité

### Architecture Sécurisée

```
Utilisateur (Internet)
    ↓
Frontend Cloud Run (PUBLIC) - Nginx
    ↓
Backend Cloud Run (PUBLIC avec JWT) - FastAPI
    ↓                     ↓                    ↓
Cloud Functions    Firestore          Cloud Storage
    (PRIVÉ)          (règles)            (CORS limité)
```

### Mesures de Sécurité

- ✅ **Authentification JWT** : Tokens expiration 7 jours, refresh automatique
- ✅ **Code d'accès rotatif** : Change automatiquement toutes les heures (Cloud Scheduler)
- ✅ **Quotas utilisateurs** : 2 vidéos max/utilisateur (Firestore)
- ✅ **CORS restreint** : Uniquement origines autorisées sur Cloud Storage
- ✅ **Firestore Rules** : Validation côté serveur des accès données
- ✅ **Service Accounts** : Permissions minimales (Least Privilege)
- ✅ **Secrets Management** : Variables d'environnement Cloud Run (pas de .env en prod)
- ✅ **Workload Identity** : GitHub Actions sans credentials JSON
- ✅ **HTTPS obligatoire** : Cloud Run force TLS 1.2+
- ✅ **Rate limiting** : Via Cloud Run (100 req/s par container)

### Firestore Security Rules

Voir [`firestore.rules`](firestore.rules) :
- Utilisateurs ne peuvent lire que leurs propres données
- Admins ont accès complet
- Validation des données côté serveur

> 🔐 **Détails complets** : [docs/architecture/AUTH_SYSTEM.md](docs/architecture/AUTH_SYSTEM.md)

---

## � Système d'Authentification

L'application dispose d'un système d'authentification complet pour protéger vos ressources :

### Fonctionnalités
- ✅ **Code d'accès rotatif** : Code de 8 caractères qui change toutes les heures
- ✅ **Authentification JWT** : Tokens sécurisés avec expiration de 7 jours
- ✅ **Système de quotas** : 2 vidéos max pour utilisateurs normaux, illimité pour admins
- ✅ **Backend privé** : API accessible uniquement via le frontend (Cloud Run authentifié)
- ✅ **Workload Identity** : Pas de credentials.json en production

### Architecture Sécurisée

```
Frontend (PUBLIC) → Nginx Proxy → Backend (PRIVÉ)
     ↓                              ↓
Service Account            Service Account
Frontend SA               Backend SA
  └─ Invoke Backend         └─ Storage Admin
                            └─ Firestore User
```

### Obtenir le Code d'Accès

Le code change automatiquement toutes les heures via Cloud Scheduler.

**Option 1 : API de Rotation**
```bash
curl https://rotate-access-code-5ranhgrf2q-uc.a.run.app/
# Retourne : {"new_code": "ABC12XYZ", "valid_until": "2026-02-12T16:00:00Z"}
```

**Option 2 : Firestore Console**
```
https://console.firebase.google.com/project/reetik-project/firestore
→ Collection: config
→ Document: access_code
→ Champ: code
```

### Flow d'Utilisation

1. 🔑 **Obtenir le code actuel** (Cloud Function ou Firestore)
2. 📝 **S'inscrire** : Email + Mot de passe + Code → JWT token
3. 🔐 **Se connecter** : Email + Mot de passe + Code → JWT token (7 jours)
4. 🎬 **Créer des vidéos** : Quota vérifié automatiquement (2/user, illimité/admin)
5. 📊 **Suivre la progression** : WebSocket temps réel + notifications
6. 📥 **Télécharger** : Cloud Storage avec URL signée (CORS activé)

## 🚀 Améliorations Futures

### ✅ Fonctionnalités Implémentées
- [x] Interface web React moderne avec WebSocket temps réel
- [x] Système d'authentification JWT avec quotas
- [x] Backend FastAPI Cloud Run avec API REST
- [x] Déploiement Terraform + CI/CD GitHub Actions
- [x] Système de retry automatique pour clips
- [x] Monitoring et rotation code d'accès
- [x] Docker Compose pour développement local
- [x] CORS Cloud Storage pour lecture vidéos

### 🔄 En Cours (Sprint Actuel)
- [ ] **Monitoring avancé** : Dashboards Cloud Monitoring + Alertes
- [ ] **Tests automatisés** : Backend (pytest) + Frontend (Playwright)
- [ ] **Optimisation coûts** : Cache Gemini, réduction taille clips

### 🎯 Roadmap Complète
Consultez **[ROADMAP.md](ROADMAP.md)** pour la feuille de route détaillée avec :
- Migration Veo 3.1 audio natif (vidéos fluides 60-141s)
- Système de personnages récurrents (Nano Banana)
- Templates styles visuels (7 styles)
- Multi-langues (FR, EN, ES, DE, IT)
- Musique de fond automatique
- Publication auto TikTok/YouTube
- Analytics avancés & A/B testing
- Monétisation (Stripe, plans Pro/Business)

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

---

## 👤 Auteur

**Linerror99**
- GitHub: [@Linerror99](https://github.com/Linerror99)
- Projet: Reetik - Génération Vidéos IA
- Stack: Google Cloud + Vertex AI (Gemini 2.5 Pro + Veo 3.1)

---

## 🙏 Remerciements

### Technologies & Services
- **Google Cloud Platform** - Infrastructure Cloud Run, Cloud Functions, Cloud Storage
- **Google DeepMind** - Gemini 2.5 Pro (génération scripts) & **Veo 3.1** (génération vidéo HD, qualité Pro)
- **Google Cloud AI** - Text-to-Speech Premium (voix naturelles)
- **OpenAI** - Whisper (transcription & synchronisation sous-titres)
- **FFmpeg** - Traitement vidéo et assemblage

### 🎥 Pourquoi Veo 3.1 ?
- **Qualité cinématique** : Rendu vidéo ultra-réaliste en HD 1080p
- **Mouvement fluide** : Transitions naturelles et cohérence temporelle améliorée
- **Précision accrue** : Meilleure compréhension des prompts complexes
- **Format vertical optimisé** : Conçu spécifiquement pour TikTok/Shorts (9:16)
- **Génération rapide** : ~30-40s par clip de 8 secondes

### Outils & Frameworks
- **FastAPI** - Framework API Python moderne
- **React + Vite** - Interface web réactive
- **Terraform** - Infrastructure as Code
- **Docker** - Containerisation
- **GitHub Actions** - CI/CD automatisé

---

## 📞 Support & Contribution

### 🐛 Signaler un Problème

1. **Vérifier la documentation** : Consultez [docs/](docs/) pour les guides détaillés
2. **Consulter les logs** : Cloud Console > Cloud Run/Functions > Logs
3. **Ouvrir une issue** : [GitHub Issues](https://github.com/votre-username/pipeline-tiktok-ia/issues)

### 💬 Questions & Discussions

- **Documentation complète** : Dossier [`docs/`](docs/)
- **API Documentation** : https://tiktok-backend-vrzs3y5aoq-uc.a.run.app/docs
- **Guides de déploiement** : [docs/deployment/](docs/deployment/)

### 🤝 Contribuer

Les contributions sont les bienvenues ! 
1. Fork le repository
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 🎬 Démarrer Maintenant

### Production (Interface Web)
👉 **https://portfolio-prod-portfolio-app-588105049123.us-west1.run.app**

### Développement Local
```bash
git clone https://github.com/votre-username/pipeline-tiktok-ia.git
cd pipeline-tiktok-ia
docker-compose up
# Frontend : http://localhost:3000
# Backend : http://localhost:8000/docs
```

**Générez votre première vidéo virale maintenant ! 🎥🔥**