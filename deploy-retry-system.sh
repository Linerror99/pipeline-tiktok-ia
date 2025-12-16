#!/bin/bash

# 🚀 Script de déploiement de l'architecture dynamique event-driven
# Déploie les agents et la fonction de monitoring

set -e  # Arrêter en cas d'erreur

PROJECT_ID="pipeline-video-ia"
REGION="us-central1"
BUCKET_NAME="tiktok-pipeline-artifacts-pipeline-video-ia"

echo "🎯 Déploiement de l'architecture event-driven"
echo "=============================================="
echo ""
echo "📋 Composants à déployer :"
echo "  1. Agent Vidéo (avec document video_status centralisé)"
echo "  2. Cloud Function Monitor (vérifie + relance + déclenche)"
echo "  3. Agent Assembleur (déclenché par HTTP)"
echo "  4. Cloud Scheduler (toutes les 2 minutes)"
echo ""
read -p "Continuer ? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# ============================================================
# 1. AGENT VIDÉO
# ============================================================
echo ""
echo "📹 [1/4] Déploiement de l'agent vidéo..."
cd agent-video

gcloud functions deploy generate-video-agent \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=. \
    --entry-point=generate_video \
    --trigger-bucket=${BUCKET_NAME} \
    --timeout=540s \
    --memory=2Gi \
    --project=${PROJECT_ID}

if [ $? -eq 0 ]; then
    echo "✅ Agent vidéo déployé"
else
    echo "❌ Erreur déploiement agent vidéo"
    exit 1
fi

cd ..

# ============================================================
# 2. AGENT ASSEMBLEUR (HTTP)
# ============================================================
echo ""
echo "🎬 [2/4] Déploiement de l'agent assembleur (HTTP)..."
cd agent-assembler

gcloud functions deploy assemble-video-agent \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=. \
    --entry-point=assemble_video \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=4Gi \
    --project=${PROJECT_ID}

if [ $? -eq 0 ]; then
    echo "✅ Agent assembleur déployé"
else
    echo "❌ Erreur déploiement agent assembleur"
    exit 1
fi

# Récupérer l'URL de l'assembleur
ASSEMBLER_URL=$(gcloud functions describe assemble-video-agent \
    --gen2 \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(serviceConfig.uri)')

echo "📍 URL de l'assembleur: ${ASSEMBLER_URL}"

cd ..

# ============================================================
# 3. CLOUD FUNCTION MONITOR
# ============================================================
echo ""
echo "🔍 [3/4] Déploiement de la fonction de monitoring..."
cd cloud-functions/monitor-and-assemble

gcloud functions deploy monitor-and-assemble \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=. \
    --entry-point=monitor_and_assemble \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=512Mi \
    --set-env-vars="AGENT_ASSEMBLER_URL=${ASSEMBLER_URL}" \
    --project=${PROJECT_ID}

if [ $? -eq 0 ]; then
    echo "✅ Fonction de monitoring déployée"
else
    echo "❌ Erreur déploiement fonction monitoring"
    exit 1
fi

# Récupérer l'URL de la fonction de monitoring
MONITOR_URL=$(gcloud functions describe monitor-and-assemble \
    --gen2 \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(serviceConfig.uri)')

echo "📍 URL du monitor: ${MONITOR_URL}"

cd ../..

# ============================================================
# 4. CLOUD SCHEDULER
# ============================================================
echo ""
echo "⏰ [4/4] Configuration du Cloud Scheduler..."

SCHEDULER_JOB_NAME="monitor-clips-job"

# Vérifier si le job existe déjà
if gcloud scheduler jobs describe ${SCHEDULER_JOB_NAME} --location=${REGION} --project=${PROJECT_ID} &>/dev/null; then
    echo "  Mise à jour du job existant..."
    gcloud scheduler jobs update http ${SCHEDULER_JOB_NAME} \
        --location=${REGION} \
        --schedule="*/2 * * * *" \
        --uri="${MONITOR_URL}" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --project=${PROJECT_ID}
else
    echo "  Création d'un nouveau job..."
    gcloud scheduler jobs create http ${SCHEDULER_JOB_NAME} \
        --location=${REGION} \
        --schedule="*/2 * * * *" \
        --uri="${MONITOR_URL}" \
        --http-method=POST \
        --headers="Content-Type=application/json" \
        --project=${PROJECT_ID} \
        --description="Vérifie les clips vidéo et déclenche l'assembleur toutes les 2 minutes"
fi

if [ $? -eq 0 ]; then
    echo "✅ Cloud Scheduler configuré"
else
    echo "❌ Erreur configuration Scheduler"
    exit 1
fi

# ============================================================
# RÉSUMÉ
# ============================================================
echo ""
echo "========================================"
echo "  🎉 Déploiement terminé avec succès !"
echo "========================================"
echo ""
echo "📊 Architecture Event-Driven déployée :"
echo ""
echo "  1️⃣  Agent Vidéo"
echo "     └─ Déclenché par: upload audio (audio_*.mp3)"
echo "     └─ Action: Lance Veo, crée video_status dans Firestore"
echo ""
echo "  2️⃣  Monitor (toutes les 2 min)"
echo "     └─ URL: ${MONITOR_URL}"
echo "     └─ Action: Vérifie clips, relance échecs, déclenche assembleur"
echo ""
echo "  3️⃣  Agent Assembleur"
echo "     └─ URL: ${ASSEMBLER_URL}"
echo "     └─ Déclenché par: Monitor (HTTP)"
echo "     └─ Action: Assemble vidéo finale, met à jour Firestore"
echo ""
echo "🔍 Monitoring :"
echo ""
echo "  Firestore Console :"
echo "    https://console.cloud.google.com/firestore/data/video_status?project=${PROJECT_ID}"
echo ""
echo "  Logs Agent Vidéo :"
echo "    gcloud functions logs read generate-video-agent --gen2 --region=${REGION} --limit=50"
echo ""
echo "  Logs Monitor :"
echo "    gcloud functions logs read monitor-and-assemble --gen2 --region=${REGION} --limit=50"
echo ""
echo "  Logs Assembleur :"
echo "    gcloud functions logs read assemble-video-agent --gen2 --region=${REGION} --limit=50"
echo ""
echo "🧪 Test manuel du monitor :"
echo "  curl -X POST ${MONITOR_URL}"
echo ""
echo "📖 Documentation : RETRY_SYSTEM.md"
