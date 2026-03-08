# ── Cloud Scheduler V3 ─────────────────────────────

# Scheduler pour polling les opérations Veo 3.1 en cours
resource "google_cloud_scheduler_job" "monitor_extensions_v3" {
  name        = "monitor-extensions-v3-scheduler"
  description = "Poll Veo 3.1 operations and launch extensions"
  schedule    = var.monitor_schedule
  time_zone   = "Europe/Paris"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.monitor_extensions_v3.service_config[0].uri

    oidc_token {
      service_account_email = google_service_account.v3_functions_sa.email
    }
  }

  retry_config {
    retry_count = 1
  }

  depends_on = [
    google_cloudfunctions2_function.monitor_extensions_v3,
    google_project_service.required_apis,
  ]
}
