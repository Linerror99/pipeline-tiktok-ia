#!/bin/bash

# Configuration
PROJECT_ID="pipeline-video-ia"
REGION="us-central1"
REPOSITORY="pipeline-tiktok"

# Couleurs pour les logs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Build et Push des images Docker vers Artifact Registry ===${NC}\n"

# Vérifier que gcloud est configuré
if ! gcloud config get-value project &> /dev/null; then
    echo -e "${RED}Erreur: gcloud n'est pas configuré. Exécutez 'gcloud auth login' et 'gcloud config set project ${PROJECT_ID}'${NC}"
    exit 1
fi

# Créer le repository Artifact Registry s'il n'existe pas
echo -e "${BLUE}1. Création du repository Artifact Registry...${NC}"
gcloud artifacts repositories create ${REPOSITORY} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Images Docker pour pipeline TikTok" \
    2>/dev/null || echo "Repository déjà existant"

# Configurer Docker pour Artifact Registry
echo -e "\n${BLUE}2. Configuration de l'authentification Docker...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Variables pour les noms d'images
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/backend"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/frontend"

# Build et push backend
echo -e "\n${BLUE}3. Build de l'image backend...${NC}"
docker build -t ${BACKEND_IMAGE}:latest ./backend

echo -e "\n${BLUE}4. Push de l'image backend...${NC}"
docker push ${BACKEND_IMAGE}:latest

# Build et push frontend
echo -e "\n${BLUE}5. Build de l'image frontend...${NC}"
docker build -t ${FRONTEND_IMAGE}:latest ./frontend

echo -e "\n${BLUE}6. Push de l'image frontend...${NC}"
docker push ${FRONTEND_IMAGE}:latest

echo -e "\n${GREEN}✓ Images poussées avec succès !${NC}"
echo -e "\nImages disponibles:"
echo -e "  - Backend:  ${BACKEND_IMAGE}:latest"
echo -e "  - Frontend: ${FRONTEND_IMAGE}:latest"
