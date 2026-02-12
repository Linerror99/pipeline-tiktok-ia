# ========================================
# Cloud Scheduler - Rotation Code d'Accès
# ========================================

# Job qui déclenche la rotation toutes les heures
resource "google_cloud_scheduler_job" "rotate_access_code_hourly" {
  name             = "rotate-access-code-hourly"
  description      = "Régénère le code d'accès toutes les heures"
  schedule         = "0 * * * *"  # Chaque heure à 0 minutes
  time_zone        = "Europe/Paris"
  attempt_deadline = "320s"
  region           = var.region

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.rotate_access_code.service_config[0].uri
    
    oidc_token {
      service_account_email = google_service_account.cloud_functions_sa.email
      audience              = google_cloudfunctions2_function.rotate_access_code.service_config[0].uri
    }
  }

  depends_on = [
    google_cloudfunctions2_function.rotate_access_code,
    google_cloudfunctions2_function_iam_member.invoker
  ]
}

# Output
output "scheduler_job_name" {
  value       = google_cloud_scheduler_job.rotate_access_code_hourly.name
  description = "Nom du job Cloud Scheduler"
}
