#!/bin/bash

# Script de déploiement de la Cloud Function et du Cloud Scheduler

PROJECT_ID="pipeline-video-ia"
REGION="us-central1"
FUNCTION_NAME="rotate-access-code"

echo "🚀 Déploiement de la Cloud Function de rotation du code..."

# Déployer la Cloud Function
gcloud functions deploy ${FUNCTION_NAME} \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=./rotate-access-code \
    --entry-point=rotate_access_code \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT=${PROJECT_ID}"

# Récupérer l'URL de la Cloud Function
FUNCTION_URL=$(gcloud functions describe ${FUNCTION_NAME} \
    --region=${REGION} \
    --gen2 \
    --format='value(serviceConfig.uri)')

echo "✅ Cloud Function déployée: ${FUNCTION_URL}"

# Créer le Cloud Scheduler job (toutes les heures à H:00)
echo ""
echo "⏰ Configuration du Cloud Scheduler..."

gcloud scheduler jobs create http rotate-access-code-job \
    --location=${REGION} \
    --schedule="0 * * * *" \
    --uri="${FUNCTION_URL}" \
    --http-method=POST \
    --description="Régénère le code d'accès toutes les heures" \
    --time-zone="Europe/Paris" \
    || echo "Job scheduler existe déjà"

echo ""
echo "✅ Configuration terminée !"
echo ""
echo "📋 Pour tester manuellement:"
echo "   gcloud scheduler jobs run rotate-access-code-job --location=${REGION}"
echo ""
echo "📋 Pour voir le code actuel dans Firestore:"
echo "   Allez sur: https://console.firebase.google.com/project/${PROJECT_ID}/firestore"
echo "   Collection: config → Document: access_code → Champ: code"
