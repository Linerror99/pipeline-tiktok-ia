# ========================================
# Cloud Run - Backend & Frontend
# ========================================

# Backend API Service
resource "google_cloud_run_v2_service" "backend" {
  name     = "tiktok-backend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_functions_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/backend:latest"

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCP_REGION"
        value = var.region
      }

      env {
        name  = "BUCKET_NAME_V2"
        value = var.bucket_name_v2
      }

      env {
        name  = "SCRIPT_AGENT_URL"
        value = "https://us-central1-${var.project_id}.cloudfunctions.net/agent-script-v2"
      }

      env {
        name  = "SECRET_KEY"
        value = var.backend_secret_key
      }

      env {
        name  = "CORS_ORIGINS"
        value = jsonencode(var.cors_origins)
      }

      # Ne pas inclure ACCESS_CODE ici - géré par rotation Cloud Function
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_artifact_registry_repository.docker_repo,
    google_project_service.required_apis
  ]
}

# IAM pour accès public au backend
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  location = google_cloud_run_v2_service.backend.location
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Frontend Static Web App
resource "google_cloud_run_v2_service" "frontend" {
  name     = "tiktok-frontend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/frontend:latest"

      ports {
        container_port = 80
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = false
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_artifact_registry_repository.docker_repo,
    google_project_service.required_apis
  ]
}

# IAM pour accès public au frontend
resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  location = google_cloud_run_v2_service.frontend.location
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "backend_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "URL du backend Cloud Run"
}

output "frontend_url" {
  value       = google_cloud_run_v2_service.frontend.uri
  description = "URL du frontend Cloud Run"
}
