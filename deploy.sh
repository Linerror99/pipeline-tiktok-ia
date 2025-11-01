#!/bin/bash

# Configuration
PROJECT_ID="pipeline-video-ia"
REGION="us-central1"
REPOSITORY="pipeline-tiktok"

# Service Accounts pour Workload Identity
BACKEND_SA="pipeline-backend-sa@${PROJECT_ID}.iam.gserviceaccount.com"
FRONTEND_SA="pipeline-frontend-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Variables d'environnement pour le backend
BUCKET_NAME="tiktok-pipeline-artifacts-pipeline-video-ia"
SCRIPT_AGENT_URL="" # À remplir avec l'URL de votre Cloud Function

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Déploiement sur Cloud Run ===${NC}\n"

# Images
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/backend:latest"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/frontend:latest"

# Déployer le backend (PRIVÉ - seulement accessible par le frontend)
echo -e "${BLUE}1. Déploiement du backend (mode sécurisé)...${NC}"
gcloud run deploy pipeline-backend \
    --image=${BACKEND_IMAGE} \
    --platform=managed \
    --region=${REGION} \
    --no-allow-unauthenticated \
    --service-account=${BACKEND_SA} \
    --set-env-vars="PROJECT_ID=${PROJECT_ID},BUCKET_NAME=${BUCKET_NAME},REGION=${REGION},SCRIPT_AGENT_URL=${SCRIPT_AGENT_URL}" \
    --memory=512Mi \
    --cpu=1 \
    --max-instances=10 \
    --port=8000

# Récupérer l'URL du backend
BACKEND_URL=$(gcloud run services describe pipeline-backend --region=${REGION} --format='value(status.url)')
echo -e "\n${GREEN}✓ Backend déployé: ${BACKEND_URL}${NC}"

# Autoriser le frontend SA à invoquer le backend
echo -e "\n${BLUE}2. Configuration des permissions d'invocation...${NC}"
gcloud run services add-iam-policy-binding pipeline-backend \
    --region=${REGION} \
    --member="serviceAccount:${FRONTEND_SA}" \
    --role="roles/run.invoker"

echo -e "${GREEN}✓ Frontend autorisé à appeler le backend${NC}"

# Déployer le frontend (PUBLIC - proxy sécurisé vers backend privé)
echo -e "\n${BLUE}3. Déploiement du frontend...${NC}"
gcloud run deploy pipeline-frontend \
    --image=${FRONTEND_IMAGE} \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --service-account=${FRONTEND_SA} \
    --set-env-vars="BACKEND_URL=${BACKEND_URL}" \
    --memory=256Mi \
    --cpu=1 \
    --max-instances=10 \
    --port=80

# Récupérer l'URL du frontend
FRONTEND_URL=$(gcloud run services describe pipeline-frontend --region=${REGION} --format='value(status.url)')
echo -e "\n${GREEN}✓ Frontend déployé: ${FRONTEND_URL}${NC}"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Déploiement sécurisé terminé ! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n📊 Architecture déployée:"
echo -e "  ├─ Backend (PRIVÉ):  ${BACKEND_URL}"
echo -e "  │  └─ Service Account: ${BACKEND_SA}"
echo -e "  │  └─ Permissions: Storage Object Admin, Token Creator"
echo -e "  │"
echo -e "  └─ Frontend (PUBLIC): ${FRONTEND_URL}"
echo -e "     └─ Service Account: ${FRONTEND_SA}"
echo -e "     └─ Peut invoquer le backend (roles/run.invoker)"
echo -e "\n🔒 Sécurité:"
echo -e "  ✓ Backend accessible uniquement par le frontend"
echo -e "  ✓ Workload Identity activé (pas de credentials.json)"
echo -e "  ✓ Frontend proxy les requêtes /api vers le backend privé"
echo -e "\n🌐 Accédez à votre application:"
echo -e "  ${FRONTEND_URL}"
