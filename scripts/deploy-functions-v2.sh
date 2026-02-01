#!/bin/bash
# Déploiement Cloud Functions V2
# Déploie agent-script, agent-video, monitor-veo31, agent-assembler

set -e

PROJECT_ID="reetik-project"
REGION="us-central1"
BUCKET_V2="tiktok-pipeline-v2-artifacts-reetik-project"

# Arguments: --skip-script pour sauter agent-script déjà déployé
SKIP_SCRIPT=false
if [[ "$1" == "--skip-script" ]]; then
    SKIP_SCRIPT=true
fi

echo "========================================="
echo "🚀 Déploiement Cloud Functions V2"
echo "========================================="
echo "Projet: ${PROJECT_ID}"
echo "Région: ${REGION}"
echo "Bucket: ${BUCKET_V2}"
echo "========================================="

# 1. Déployer agent-script V2 (HTTP - appelé par Backend API)
if [ "$SKIP_SCRIPT" = false ]; then
    echo ""
    echo "📝 1/4 Déploiement agent-script V2 (HTTP trigger)..."

    gcloud functions deploy agent-script-v2 \
        --gen2 \
        --runtime=python312 \
        --region=${REGION} \
        --source=./agent-script \
        --entry-point=generate_script \
        --trigger-http \
        --allow-unauthenticated \
        --set-env-vars GCP_PROJECT=${PROJECT_ID},BUCKET_NAME=${BUCKET_V2} \
        --memory=512MB \
        --timeout=540s

    echo "  ✓ agent-script-v2 déployé (HTTP)"
else
    echo ""
    echo "⏭️  1/4 Agent-script V2 ignoré (--skip-script)"
fi

# 2. Déployer agent-video V2 (Cloud Storage trigger - script_v2.json)
echo ""
echo "🎬 2/4 Déploiement agent-video V2 (Storage trigger)..."

gcloud functions deploy agent-video-v2 \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=./agent-video \
    --entry-point=generate_video_v2 \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=${BUCKET_V2}" \
    --trigger-location=${REGION} \
    --set-env-vars GCP_PROJECT=${PROJECT_ID},BUCKET_NAME=${BUCKET_V2} \
    --memory=2GB \
    --timeout=540s

echo "  ✓ agent-video-v2 déployé (Storage trigger sur ${BUCKET_V2})"

# 3. Déployer check-and-retry-clips (HTTP - appelé par Cloud Scheduler)
echo ""
echo "🔍 3/5 Déploiement check-and-retry-clips (HTTP trigger)..."

gcloud functions deploy check-and-retry-clips \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=./cloud-functions/check-and-retry-clips \
    --entry-point=check_and_retry_clips \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT=${PROJECT_ID},BUCKET_NAME_V2=${BUCKET_V2},AGENT_ASSEMBLER_URL=https://${REGION}-${PROJECT_ID}.cloudfunctions.net/agent-assembler-v2 \
    --memory=1GB \
    --timeout=540s

echo "  ✓ check-and-retry-clips déployé (HTTP)"

# 4. Déployer agent-assembler V2 (HTTP - appelé par check-and-retry-clips)
echo ""
echo "🎞️ 4/5 Déploiement agent-assembler V2 (HTTP trigger)..."

gcloud functions deploy agent-assembler-v2 \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=./agent-assembler \
    --entry-point=assemble_video \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars GCP_PROJECT=${PROJECT_ID},BUCKET_NAME_V2=${BUCKET_V2} \
    --memory=2GB \
    --timeout=540s

echo "  ✓ agent-assembler-v2 déployé (HTTP)"

# 5. Créer Cloud Scheduler pour check-and-retry-clips
echo ""
echo "⏰ 5/5 Configuration Cloud Scheduler..."

CHECK_RETRY_URL="https://${REGION}-${PROJECT_ID}.cloudfunctions.net/check-and-retry-clips"

# Vérifier si le job existe
if gcloud scheduler jobs describe check-and-retry-clips --location=${REGION} 2>/dev/null; then
    echo "  ⚠️  Job Cloud Scheduler existe déjà, mise à jour..."
    gcloud scheduler jobs update http check-and-retry-clips \
        --location=${REGION} \
        --schedule="*/5 * * * *" \
        --uri="${CHECK_RETRY_URL}" \
        --http-method=POST \
        --headers="Content-Type=application/json"
else
    echo "  📅 Création job Cloud Scheduler..."
    gcloud scheduler jobs create http check-and-retry-clips \
        --location=${REGION} \
        --schedule="*/5 * * * *" \
        --uri="${CHECK_RETRY_URL}" \
        --http-method=POST \
        --headers="Content-Type=application/json"
fi

echo "  ✓ Cloud Scheduler configuré (toutes les 5 minutes)"

# Récapitulatif
echo ""
echo "========================================="
echo "✅ Déploiement terminé !"
echo "========================================="
echo ""
echo "URLs des Cloud Functions:"
echo "  agent-script-v2:        https://${REGION}-${PROJECT_ID}.cloudfunctions.net/agent-script-v2"
echo "  agent-video-v2:         https://${REGION}-${PROJECT_ID}.cloudfunctions.net/agent-video-v2"
echo "  check-and-retry-clips:  https://${REGION}-${PROJECT_ID}.cloudfunctions.net/check-and-retry-clips"
echo "  agent-assembler-v2:     https://${REGION}-${PROJECT_ID}.cloudfunctions.net/agent-assembler-v2"
echo ""
echo "Cloud Scheduler:"
echo "  Job: check-and-retry-clips (toutes les 5 minutes)"
echo ""
echo "Pour tester:"
echo "  python test_flow_real_v2.py --theme 'Test V2' --duration 24"
echo ""
