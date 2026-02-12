# Docker Setup - V2.1 (Local Development)

## 🐳 Prérequis

- Docker Desktop installé
- Fichier `backend/credentials.json` (service account GCP)

## 🚀 Démarrage Rapide

### Option 1: Script automatique (Linux/Mac/Git Bash)
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Commandes manuelles
```bash
# Build et démarrer
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

## 📍 URLs des Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## 🔧 Configuration

Les variables d'environnement sont dans `docker-compose.yml`:

**Backend**:
- `ACCESS_CODE`: Code d'accès API (doit correspondre au frontend)
- `SECRET_KEY`: Clé JWT (min 32 caractères)
- `AGENT_SCRIPT_V2_URL`: URL de la Cloud Function

**Frontend** (build args):
- `VITE_API_URL`: URL backend (http://localhost:8000)
- `VITE_WS_URL`: URL WebSocket (ws://localhost:8000)
- `VITE_ACCESS_CODE`: Doit correspondre au backend

## 🔑 Service Account Credentials

**IMPORTANT**: Placez votre fichier de credentials GCP:
```
backend/credentials.json
```

Ce fichier est nécessaire pour:
- Accès à Cloud Storage
- Accès à Firestore
- Appels aux Cloud Functions

## 📊 Commandes Utiles

### Logs
```bash
# Tous les services
docker-compose logs -f

# Backend uniquement
docker-compose logs -f backend

# Frontend uniquement
docker-compose logs -f frontend
```

### Rebuild
```bash
# Rebuild tout
docker-compose build --no-cache
docker-compose up -d

# Rebuild un service
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Shell dans les containers
```bash
# Backend
docker exec -it tiktok-backend sh

# Frontend
docker exec -it tiktok-frontend sh
```

### Restart
```bash
docker-compose restart
```

### Cleanup
```bash
# Arrêter et supprimer tout
docker-compose down -v

# Nettoyer Docker complètement
docker system prune -a
```

## 🧪 Tests Sans Génération Vidéo

### 1. Health Check Backend
```bash
curl http://localhost:8000/
```
Attendu: `{"message": "Backend API v2.1.0", "status": "healthy"}`

### 2. Test Frontend
Ouvrir: http://localhost:3000

### 3. Test API Docs
Ouvrir: http://localhost:8000/docs

### 4. Test Liste Vidéos (avec token)
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass"

# Récupérer le token et tester
curl http://localhost:8000/videos \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🐛 Troubleshooting

### Port déjà utilisé
Changez le port dans `docker-compose.yml`:
```yaml
ports:
  - "3001:80"  # Frontend
  - "8001:8000"  # Backend
```

### Credentials manquants
```bash
# Vérifier
ls -la backend/credentials.json

# Alternative: utiliser gcloud CLI
gcloud auth application-default login
```

### Build échoue
```bash
# Nettoyer et rebuild
docker system prune -a
docker-compose build --no-cache
```

### Container crash
```bash
# Voir les logs
docker-compose logs backend
docker-compose logs frontend

# Vérifier la config
docker-compose config
```

## 📦 Structure

```
.
├── backend/
│   ├── Dockerfile
│   ├── credentials.json    # GCP credentials (NON VERSIONNÉ)
│   └── app/
├── frontend-v2/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── .dockerignore
│   └── src/
├── docker-compose.yml      # Configuration locale
└── start.sh               # Script de démarrage
```

## 🚢 Déploiement Cloud Run (À FAIRE)

```bash
# Backend
cd backend
gcloud run deploy backend-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
cd frontend-v2
gcloud run deploy frontend-v2 \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## ⚙️ Production Considerations

1. **Secrets Management**: Utiliser Cloud Secret Manager au lieu de variables d'environnement
2. **CORS**: Configurer avec les vraies URLs de production
3. **SSL/TLS**: Cloud Run gère automatiquement HTTPS
4. **Scaling**: Configurer min/max instances dans Cloud Run
5. **Monitoring**: Activer Cloud Monitoring et Logging

---

**Version**: 2.1.0  
**Date**: February 2026
