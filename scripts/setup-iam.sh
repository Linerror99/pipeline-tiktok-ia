#!/bin/bash

# Script de configuration IAM et Workload Identity pour Cloud Run
# Ce script configure les service accounts et permissions nécessaires

# Configuration
PROJECT_ID="reetik-project"
REGION="us-central1"
BACKEND_SA="pipeline-backend-sa"
FRONTEND_SA="pipeline-frontend-sa"
BUCKET_NAME="tiktok-pipeline-artifacts-reetik-project"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Configuration IAM et Workload Identity ===${NC}\n"

# Vérifier que gcloud est configuré
if ! gcloud config get-value project &> /dev/null; then
    echo -e "${RED}Erreur: gcloud n'est pas configuré${NC}"
    exit 1
fi

# 1. Créer le service account pour le backend
echo -e "${BLUE}1. Création du service account backend...${NC}"
gcloud iam service-accounts create ${BACKEND_SA} \
    --display-name="Service Account pour Backend Cloud Run" \
    --description="Utilisé par le backend pour accéder à GCS et autres services Google Cloud" \
    2>/dev/null || echo "Service account backend existe déjà"

BACKEND_SA_EMAIL="${BACKEND_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

# 2. Donner les permissions nécessaires au backend SA
echo -e "\n${BLUE}2. Attribution des permissions au backend SA...${NC}"

# Permission pour GCS (lire/écrire/signer URLs)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${BACKEND_SA_EMAIL}" \
    --role="roles/storage.objectAdmin" \
    --condition=None

# Permission pour créer des signed URLs
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${BACKEND_SA_EMAIL}" \
    --role="roles/iam.serviceAccountTokenCreator" \
    --condition=None

echo -e "${GREEN}✓ Permissions backend configurées${NC}"

# 3. Créer le service account pour le frontend
echo -e "\n${BLUE}3. Création du service account frontend...${NC}"
gcloud iam service-accounts create ${FRONTEND_SA} \
    --display-name="Service Account pour Frontend Cloud Run" \
    --description="Utilisé par le frontend pour appeler le backend de manière sécurisée" \
    2>/dev/null || echo "Service account frontend existe déjà"

FRONTEND_SA_EMAIL="${FRONTEND_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${GREEN}✓ Service accounts créés${NC}"

# 4. Afficher les informations
echo -e "\n${GREEN}=== Configuration terminée ===${NC}"
echo -e "\nService Accounts créés:"
echo -e "  Backend:  ${BACKEND_SA_EMAIL}"
echo -e "  Frontend: ${FRONTEND_SA_EMAIL}"

echo -e "\n${YELLOW}Prochaines étapes:${NC}"
echo -e "1. Déployez le backend avec: --service-account=${BACKEND_SA_EMAIL}"
echo -e "2. Donnez au frontend le droit d'invoquer le backend (fait automatiquement par deploy.sh)"
echo -e "3. Le backend utilisera Workload Identity (pas besoin de credentials.json en prod)"

echo -e "\n${BLUE}Commandes pour déployer:${NC}"
echo -e "  ./build-and-push.sh    # Build et push les images"
echo -e "  ./deploy.sh            # Déploie avec Workload Identity"
