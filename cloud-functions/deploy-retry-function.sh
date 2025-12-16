#!/bin/bash

# Script pour déployer la Cloud Function de retry des clips vidéo
# et configurer un Cloud Scheduler pour l'exécuter toutes les 10 minutes

PROJECT_ID="pipeline-video-ia"
REGION="us-central1"
FUNCTION_NAME="check-and-retry-clips"
SCHEDULER_JOB_NAME="retry-clips-scheduler"

echo "🚀 Déploiement de la Cloud Function de retry..."

# Déployer la Cloud Function (Gen 2)
gcloud functions deploy ${FUNCTION_NAME} \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=./check-and-retry-clips \
    --entry-point=check_and_retry_clips \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=512Mi \
    --project=${PROJECT_ID}

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du déploiement de la Cloud Function"
    exit 1
fi

echo "✅ Cloud Function déployée"

# Récupérer l'URL de la Cloud Function
FUNCTION_URL=$(gcloud functions describe ${FUNCTION_NAME} \
    --gen2 \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(serviceConfig.uri)')

echo "📍 URL de la fonction: ${FUNCTION_URL}"

# Créer ou mettre à jour le Cloud Scheduler job
echo "⏰ Configuration du Cloud Scheduler..."

# Vérifier si le job existe déjà
if gcloud scheduler jobs describe ${SCHEDULER_JOB_NAME} --location=${REGION} --project=${PROJECT_ID} &>/dev/null; then
    echo "  Mise à jour du job existant..."
    gcloud scheduler jobs update http ${SCHEDULER_JOB_NAME} \
        --location=${REGION} \
        --schedule="*/10 * * * *" \
        --uri="${FUNCTION_URL}" \
        --http-method=GET \
        --project=${PROJECT_ID}
else
    echo "  Création d'un nouveau job..."
    gcloud scheduler jobs create http ${SCHEDULER_JOB_NAME} \
        --location=${REGION} \
        --schedule="*/10 * * * *" \
        --uri="${FUNCTION_URL}" \
        --http-method=GET \
        --project=${PROJECT_ID} \
        --description="Vérifie et relance les clips vidéo qui ont échoué toutes les 10 minutes"
fi

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la configuration du Scheduler"
    exit 1
fi

echo "✅ Cloud Scheduler configuré"
echo ""
echo "=========================================="
echo "  Déploiement terminé ! 🎉"
echo "=========================================="
echo ""
echo "📊 Configuration:"
echo "  Function: ${FUNCTION_NAME}"
echo "  URL: ${FUNCTION_URL}"
echo "  Schedule: Toutes les 10 minutes"
echo ""
echo "🧪 Test manuel:"
echo "  curl ${FUNCTION_URL}"
echo ""
echo "📝 Logs:"
echo "  gcloud functions logs read ${FUNCTION_NAME} --gen2 --region=${REGION} --limit=50"
