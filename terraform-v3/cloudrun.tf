# ── Cloud Run — Backend V3 ─────────────────────────

resource "google_cloud_run_v2_service" "backend_v3" {
  name     = "backend-v3"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/reetik-v3/backend-v3:latest"

      ports {
        container_port = 8080
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "FIRESTORE_DATABASE"
        value = var.firestore_database_id
      }
      env {
        name  = "REGION"
        value = var.region
      }
      env {
        name  = "BUCKET_NAME_V3"
        value = var.bucket_artifacts_v3
      }
      env {
        name  = "BUCKET_UPLOADS_V3"
        value = var.bucket_uploads_v3
      }
      env {
        name  = "BUCKET_THUMBNAILS_V3"
        value = var.bucket_thumbnails_v3
      }
      env {
        name  = "JWT_SECRET_KEY"
        value = var.backend_secret_key
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    service_account = google_service_account.v3_functions_sa.email
  }

  depends_on = [google_project_service.required_apis]
}

# Allow unauthenticated access to backend (auth is handled by Firebase + JWT)
resource "google_cloud_run_v2_service_iam_member" "backend_v3_public" {
  name     = google_cloud_run_v2_service.backend_v3.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Artifact Registry for V3 Docker images
resource "google_artifact_registry_repository" "v3_repo" {
  location      = var.region
  repository_id = "reetik-v3"
  format        = "DOCKER"
  description   = "Reetik V3 Docker images"

  depends_on = [google_project_service.required_apis]
}
