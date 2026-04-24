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

# ── Buckets V3 ─────────────────────────────────────────────────────────────

# Bucket principal V3 : vidéos générées + scripts Veo 3.1
# Structure : {video_id}/script_v3.json | {video_id}/clip_N.mp4 | {video_id}/final.mp4
resource "google_storage_bucket" "artifacts_v3" {
  name          = var.bucket_name_v3
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  cors {
    origin          = ["https://reetik-frontend-v3.run.app", "http://localhost:3000"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Content-Length", "Accept-Ranges", "Content-Range"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    condition { age = 180 }
    action    { type = "Delete" }
  }

  depends_on = [google_project_service.required_apis]
}

# Bucket uploads V3 : fichiers utilisateurs + images personnages
# Structure : {project_id}/{file_id}_{filename} | characters/{character_id}/image_N.png
resource "google_storage_bucket" "uploads_v3" {
  name          = var.bucket_uploads_v3
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 90 }
    action    { type = "Delete" }
  }

  depends_on = [google_project_service.required_apis]
}

# Bucket thumbnails V3 : miniatures des vidéos
# Structure : {video_id}/thumbnail.png
resource "google_storage_bucket" "thumbnails_v3" {
  name          = var.bucket_thumbnails_v3
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  cors {
    origin          = ["https://reetik-frontend-v3.run.app", "http://localhost:3000"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }

  depends_on = [google_project_service.required_apis]
}

# IAM V3 — service account des agents a accès en lecture/écriture
resource "google_storage_bucket_iam_member" "artifacts_v3_sa_access" {
  bucket = google_storage_bucket.artifacts_v3.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

resource "google_storage_bucket_iam_member" "uploads_v3_sa_access" {
  bucket = google_storage_bucket.uploads_v3.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

resource "google_storage_bucket_iam_member" "thumbnails_v3_sa_access" {
  bucket = google_storage_bucket.thumbnails_v3.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

# tiktok-pipeline-sa a besoin de storage.legacyBucketReader pour bucket.exists() + Veo output
resource "google_storage_bucket_iam_member" "artifacts_v3_tiktok_sa_reader" {
  bucket = google_storage_bucket.artifacts_v3.name
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:tiktok-pipeline-sa@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "artifacts_v3_tiktok_sa_writer" {
  bucket = google_storage_bucket.artifacts_v3.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:tiktok-pipeline-sa@${var.project_id}.iam.gserviceaccount.com"
}
