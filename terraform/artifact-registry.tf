# ========================================
# Artifact Registry
# ========================================

# Repository pour les images Docker
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "tiktok-pipeline"
  description   = "Docker repository for TikTok Pipeline application"
  format        = "DOCKER"

  cleanup_policy_dry_run = false
  cleanup_policies {
    id     = "keep-minimum-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = 5
    }
  }

  depends_on = [google_project_service.required_apis]
}

# IAM pour permettre au service account de push/pull des images
resource "google_artifact_registry_repository_iam_member" "docker_repo_writer" {
  location   = google_artifact_registry_repository.docker_repo.location
  repository = google_artifact_registry_repository.docker_repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

# Output
output "docker_repo_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
  description = "URL du repository Docker dans Artifact Registry"
}
