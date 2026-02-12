#!/bin/bash
# Script pour créer le bucket V2 et les ressources nécessaires

set -e

PROJECT_ID="reetik-project"
LOCATION="us-central1"
BUCKET_V2="tiktok-pipeline-v2-artifacts"

echo "========================================="
echo "🚀 Setup Infrastructure V2"
echo "========================================="

# 1. Créer bucket V2
echo ""
echo "📦 Création bucket V2..."
if gcloud storage buckets describe gs://${BUCKET_V2} 2>/dev/null; then
    echo "  ✓ Bucket ${BUCKET_V2} existe déjà"
else
    gcloud storage buckets create gs://${BUCKET_V2} --location=${LOCATION}
    echo "  ✓ Bucket ${BUCKET_V2} créé"
fi

# 2. Définir lifecycle pour nettoyage auto (90 jours)
echo ""
echo "🗑️ Configuration lifecycle bucket..."
cat > /tmp/lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gcloud storage buckets update gs://${BUCKET_V2} --lifecycle-file=/tmp/lifecycle.json
echo "  ✓ Lifecycle configuré (suppression auto 90j)"

# 3. Activer versioning (sécurité)
echo ""
echo "🔒 Activation versioning..."
gcloud storage buckets update gs://${BUCKET_V2} --versioning
echo "  ✓ Versioning activé"

# 4. Définir CORS pour accès frontend
echo ""
echo "🌐 Configuration CORS..."
cat > /tmp/cors.json <<EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gcloud storage buckets update gs://${BUCKET_V2} --cors-file=/tmp/cors.json
echo "  ✓ CORS configuré"

# 5. Permissions publiques en lecture (optionnel)
echo ""
echo "📖 Configuration permissions..."
# Décommenter si vous voulez rendre les vidéos finales publiques
# gcloud storage buckets add-iam-policy-binding gs://${BUCKET_V2} \
#   --member=allUsers --role=roles/storage.objectViewer
echo "  ⚠️  Bucket privé (décommenter dans le script pour rendre public)"

echo ""
echo "========================================="
echo "✅ Infrastructure V2 prête !"
echo "========================================="
echo ""
echo "Bucket: gs://${BUCKET_V2}"
echo ""
echo "Variables d'environnement à configurer:"
echo "  BUCKET_NAME=${BUCKET_V2}"
echo "  BUCKET_NAME_V2=${BUCKET_V2}"
echo ""
