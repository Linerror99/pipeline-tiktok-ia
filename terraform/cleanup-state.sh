#!/bin/bash
# Script de nettoyage du state Terraform
# Supprime les ressources qui ne sont plus gérées par Terraform

set -e

echo "========================================="
echo "🧹 Nettoyage du state Terraform"
echo "========================================="

cd "$(dirname "$0")"

echo ""
echo "📋 Suppression des Cloud Functions..."
terraform state rm google_cloudfunctions2_function.agent_script_v2 2>/dev/null || echo "  ⏭️  agent_script_v2 déjà supprimé"
terraform state rm google_cloudfunctions2_function.agent_video_v2 2>/dev/null || echo "  ⏭️  agent_video_v2 déjà supprimé"
terraform state rm google_cloudfunctions2_function.check_and_retry_clips 2>/dev/null || echo "  ⏭️  check_and_retry_clips déjà supprimé"
terraform state rm google_cloudfunctions2_function.agent_assembler_v2 2>/dev/null || echo "  ⏭️  agent_assembler_v2 déjà supprimé"

echo ""
echo "🔐 Suppression des IAM des fonctions..."
terraform state rm google_cloudfunctions2_function_iam_member.agent_script_v2_invoker 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_cloudfunctions2_function_iam_member.agent_video_v2_invoker 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_cloudfunctions2_function_iam_member.check_retry_invoker 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_cloudfunctions2_function_iam_member.agent_assembler_v2_invoker 2>/dev/null || echo "  ⏭️  Déjà supprimé"

echo ""
echo "📦 Suppression des objets bucket source..."
terraform state rm google_storage_bucket_object.agent_script_v2_source 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_storage_bucket_object.agent_video_v2_source 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_storage_bucket_object.check_retry_source 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_storage_bucket_object.agent_assembler_v2_source 2>/dev/null || echo "  ⏭️  Déjà supprimé"

echo ""
echo "🗑️  Suppression du bucket functions_source..."
terraform state rm google_storage_bucket.functions_source 2>/dev/null || echo "  ⏭️  Déjà supprimé"

echo ""
echo "🗑️  Suppression du bucket V1..."
terraform state rm google_storage_bucket.artifacts_v1 2>/dev/null || echo "  ⏭️  Déjà supprimé"
terraform state rm google_storage_bucket_iam_member.functions_v1_access 2>/dev/null || echo "  ⏭️  Déjà supprimé"

echo ""
echo "📅 Suppression du Cloud Scheduler..."
terraform state rm google_cloud_scheduler_job.check_and_retry 2>/dev/null || echo "  ⏭️  Déjà supprimé"

echo ""
echo "========================================="
echo "✅ Nettoyage terminé!"
echo "========================================="
echo ""
echo "Prochaines étapes:"
echo "1. terraform plan   # Vérifier les changements"
echo "2. terraform apply  # Appliquer la nouvelle config"
echo ""
