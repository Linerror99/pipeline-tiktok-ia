# Cloud Scheduler Jobs

# Job pour check-and-retry-clips (chaque minute)
resource "google_cloud_scheduler_job" "check_and_retry" {
  name             = "check-and-retry-clips"
  description      = "Check and retry failed video operations (V1 + V2)"
  schedule         = "* * * * *" # Every minute
  time_zone        = "UTC"
  attempt_deadline = "540s"
  region           = var.region
  
  retry_config {
    retry_count = 3
  }
  
  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.check_and_retry_clips.service_config[0].uri
    
    oidc_token {
      service_account_email = google_service_account.cloud_functions_sa.email
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_cloudfunctions2_function.check_and_retry_clips
  ]
}
