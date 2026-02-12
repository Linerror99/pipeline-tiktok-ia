# Cloud Storage Buckets

# Bucket V2 (Veo 3.1) - UNIQUEMENT CELUI-CI
resource "google_storage_bucket" "artifacts_v2" {
  name          = var.bucket_name_v2
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  # CORS configuration pour permettre la lecture des vidéos depuis le frontend
  cors {
    origin          = ["https://tiktok-frontend-838433433731.us-central1.run.app", "http://localhost:3000", "http://localhost:5173"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Content-Length", "Accept-Ranges", "Content-Range"]
    max_age_seconds = 3600
  }
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  depends_on = [google_project_service.required_apis]
}

# IAM pour le bucket V2
resource "google_storage_bucket_iam_member" "functions_v2_access" {
  bucket = google_storage_bucket.artifacts_v2.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

# IAM pour permettre la lecture publique des vidéos (nécessaire pour CORS)
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.artifacts_v2.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
