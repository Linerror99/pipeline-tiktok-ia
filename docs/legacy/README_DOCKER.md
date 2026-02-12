# TikTok Pipeline V2.1 - Local Development

## 🚀 Démarrage Rapide

### Prérequis
- Docker Desktop
- Credentials GCP dans `backend/credentials.json`

### Lancer l'application
```bash
# Linux/Mac/Git Bash
./start.sh

# Ou manuellement
docker-compose up -d --build
```

### Accéder à l'application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Voir les logs
```bash
docker-compose logs -f
```

### Arrêter
```bash
docker-compose down
```

## 📚 Documentation Complète

- [DOCKER_README.md](DOCKER_README.md) - Guide Docker complet
- [frontend-v2/README_V2.1.md](frontend-v2/README_V2.1.md) - Guide V2.1 détaillé
- [V2.1_MIGRATION.md](V2.1_MIGRATION.md) - Guide de migration

## 🎯 Version

**V2.1.0** - React TypeScript + WebSocket + Firestore V2
