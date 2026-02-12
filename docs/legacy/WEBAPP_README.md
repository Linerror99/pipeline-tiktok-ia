# 🎬 Pipeline Vidéo IA - Interface Web

Interface web complète pour gérer la génération automatique de vidéos TikTok/Shorts avec IA.

## 📋 Structure du Projet

```
pipeline-tiktok-ia/
├── frontend/                 # Application React
│   ├── src/
│   │   ├── components/      # Composants réutilisables
│   │   ├── pages/           # Pages de l'application
│   │   └── App.jsx
│   ├── Dockerfile
│   └── package.json
├── backend/                  # API FastAPI
│   ├── app/
│   │   ├── routers/         # Routes API
│   │   ├── services/        # Services métier
│   │   ├── config.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml        # Production
└── docker-compose.dev.yml    # Développement
```

## 🚀 Démarrage Rapide

### Option 1 : Développement Local (sans Docker)

#### Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos informations GCP

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible sur : http://localhost:8000
Documentation API : http://localhost:8000/docs

#### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

L'interface sera accessible sur : http://localhost:5173

### Option 2 : Développement avec Docker Compose

```bash
# Lancer tous les services en mode développement
docker-compose -f docker-compose.dev.yml up

# En arrière-plan
docker-compose -f docker-compose.dev.yml up -d

# Arrêter les services
docker-compose -f docker-compose.dev.yml down
```

- Frontend : http://localhost:5173
- Backend : http://localhost:8000

### Option 3 : Production avec Docker

```bash
# Build et lancer
docker-compose up --build

# En arrière-plan
docker-compose up -d

# Arrêter
docker-compose down
```

- Frontend : http://localhost
- Backend : http://localhost:8000

## ⚙️ Configuration

### Backend (.env)

Créez un fichier `.env` dans le dossier `backend/` :

```env
# Google Cloud Configuration
PROJECT_ID=pipeline-video-ia
BUCKET_NAME=tiktok-pipeline-artifacts-pipeline-video-ia
REGION=us-central1

# Cloud Function URL (votre agent-script déployé)
SCRIPT_AGENT_URL=https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/generate-script-agent

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Authentification Google Cloud

Le backend a besoin des credentials GCP pour accéder à Cloud Storage :

```bash
# Se connecter à GCP
gcloud auth application-default login

# Ou définir la variable d'environnement
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## 📱 Fonctionnalités

### ✅ Phase 1 (Actuelle)

- **Créer une Vidéo** : Interface pour soumettre un thème et générer une vidéo
- **Mes Vidéos** : Galerie des vidéos générées avec statut et téléchargement

### 🚧 Phase 2 (À venir)

- **Dashboard** : Statistiques et métriques
- **Logs & Monitoring** : Suivi en temps réel de la pipeline

### 🔐 Phase 3 (Future)

- **Authentification** : Connexion et gestion de compte

## 🛠️ Technologies

### Frontend
- **React 18** avec Vite
- **Tailwind CSS** pour le styling
- **React Router** pour la navigation
- **Axios** pour les appels API
- **Lucide React** pour les icônes

### Backend
- **FastAPI** (Python 3.12)
- **Google Cloud Storage** client
- **Pydantic** pour la validation
- **Uvicorn** comme serveur ASGI

### Infrastructure
- **Docker** & **Docker Compose**
- **Nginx** (frontend en production)

## 📡 API Endpoints

### Vidéos

```
POST   /api/videos/create          # Créer une nouvelle vidéo
GET    /api/videos                 # Lister toutes les vidéos
GET    /api/videos/{id}/status     # Statut d'une vidéo
GET    /api/videos/{id}/download   # URL de téléchargement
```

### Health Checks

```
GET    /                           # Info API
GET    /health                     # Health check
GET    /docs                       # Documentation interactive
```

## 🐳 Déploiement sur Cloud Run

### Build et Push des Images

```bash
# Variables
export PROJECT_ID=pipeline-video-ia
export REGION=us-central1

# Backend
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/pipeline-backend

# Frontend
cd ../frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/pipeline-frontend
```

### Déployer sur Cloud Run

```bash
# Backend API
gcloud run deploy pipeline-backend \
  --image gcr.io/$PROJECT_ID/pipeline-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=$PROJECT_ID,BUCKET_NAME=tiktok-pipeline-artifacts-$PROJECT_ID

# Frontend
gcloud run deploy pipeline-frontend \
  --image gcr.io/$PROJECT_ID/pipeline-frontend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated
```

## 🧪 Tester l'Application

### Test du Backend

```bash
# Health check
curl http://localhost:8000/health

# Créer une vidéo
curl -X POST http://localhost:8000/api/videos/create \
  -H "Content-Type: application/json" \
  -d '{"theme": "Les mystères des pyramides"}'

# Lister les vidéos
curl http://localhost:8000/api/videos
```

### Test du Frontend

1. Ouvrir http://localhost:5173
2. Aller sur "Créer"
3. Entrer un thème
4. Cliquer sur "Générer ma vidéo TikTok"
5. Vérifier dans "Mes Vidéos"

## 📝 Notes de Développement

### Hot Reload

- **Frontend** : Modification automatique des fichiers React (Vite HMR)
- **Backend** : Rechargement automatique avec `--reload` (uvicorn)

### Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Local
# Backend : logs dans le terminal uvicorn
# Frontend : logs dans le terminal Vite et la console du navigateur
```

## 🤝 Contribution

Structure de développement :

1. Créer une branche : `git checkout -b feature/ma-fonctionnalite`
2. Développer et tester localement
3. Commit : `git commit -m "feat: ajout de ma fonctionnalité"`
4. Push et créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

---

**Propulsé par** : Gemini 2.5 Pro • Veo 3.0 • Google Cloud Platform
