# ── Cloud Storage Buckets V3 ───────────────────────

# Bucket vidéos (artifacts Veo 3.1)
resource "google_storage_bucket" "v3_artifacts" {
  name          = var.bucket_artifacts_v3
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  cors {
    origin          = var.cors_origins
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type", "Content-Length", "Accept-Ranges", "Content-Range"]
    max_age_seconds = 3600
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition { age = 90 }
    action { type = "Delete" }
  }

  depends_on = [google_project_service.required_apis]
}

# Bucket uploads (fichiers utilisateur, images personnages)
resource "google_storage_bucket" "v3_uploads" {
  name          = var.bucket_uploads_v3
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 180 }
    action { type = "Delete" }
  }

  depends_on = [google_project_service.required_apis]
}

# Bucket thumbnails (Imagen 4)
resource "google_storage_bucket" "v3_thumbnails" {
  name          = var.bucket_thumbnails_v3
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  cors {
    origin          = var.cors_origins
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    condition { age = 365 }
    action { type = "Delete" }
  }

  depends_on = [google_project_service.required_apis]
}

# ── IAM Buckets ────────────────────────────────────

resource "google_storage_bucket_iam_member" "v3_artifacts_admin" {
  bucket = google_storage_bucket.v3_artifacts.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.v3_functions_sa.email}"
}

resource "google_storage_bucket_iam_member" "v3_uploads_admin" {
  bucket = google_storage_bucket.v3_uploads.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.v3_functions_sa.email}"
}

resource "google_storage_bucket_iam_member" "v3_thumbnails_admin" {
  bucket = google_storage_bucket.v3_thumbnails.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.v3_functions_sa.email}"
}
