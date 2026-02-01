output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "bucket_v2_name" {
  description = "V2 Artifacts Bucket Name"
  value       = google_storage_bucket.artifacts_v2.name
}

output "service_account_email" {
  description = "Service Account Email"
  value       = google_service_account.cloud_functions_sa.email
}

output "deployment_instructions" {
  description = "Instructions pour déployer les Cloud Functions"
  value       = <<-EOT
    
    ✅ Infrastructure de base déployée !
    
    📦 Bucket: ${google_storage_bucket.artifacts_v2.name}
    👤 Service Account: ${google_service_account.cloud_functions_sa.email}
    
    📝 Prochaines étapes - Déploiements manuels:
    
    1. Cloud Functions:
       cd ..
       ./deploy-functions-v2.sh
    
    2. Cloud Scheduler:
       cd cloud-functions
       ./deploy-scheduler.sh
    
    Les fonctions seront disponibles aux URLs:
    - https://us-central1-${var.project_id}.cloudfunctions.net/agent-script-v2
    - https://us-central1-${var.project_id}.cloudfunctions.net/agent-video-v2
    - https://us-central1-${var.project_id}.cloudfunctions.net/check-and-retry-clips
    - https://us-central1-${var.project_id}.cloudfunctions.net/agent-assembler-v2
  EOT
}
