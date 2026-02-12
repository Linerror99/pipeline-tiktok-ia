# ========================================
# Cloud Function - Rotation Code d'Accès
# ========================================

# Bucket pour le code source de la fonction
resource "google_storage_bucket" "function_source" {
  name                        = "${var.project_id}-function-source"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

# Archive du code source
data "archive_file" "rotate_access_code_source" {
  type        = "zip"
  source_dir  = "${path.module}/../cloud-functions/rotate-access-code"
  output_path = "${path.module}/.terraform/archives/rotate-access-code.zip"
}

# Upload du code dans le bucket
resource "google_storage_bucket_object" "rotate_access_code_archive" {
  name   = "rotate-access-code-${data.archive_file.rotate_access_code_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.rotate_access_code_source.output_path
}

# Cloud Function Gen2
resource "google_cloudfunctions2_function" "rotate_access_code" {
  name        = "rotate-access-code"
  location    = var.region
  description = "Régénère le code d'accès toutes les heures"

  build_config {
    runtime     = "python312"
    entry_point = "rotate_access_code"
    
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.rotate_access_code_archive.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    min_instance_count    = 0
    available_memory      = "256M"
    timeout_seconds       = 60
    service_account_email = google_service_account.cloud_functions_sa.email
    
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }
}

# IAM pour permettre l'invocation sans auth (sera appelé par Cloud Scheduler avec service account)
resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = google_cloudfunctions2_function.rotate_access_code.project
  location       = google_cloudfunctions2_function.rotate_access_code.location
  cloud_function = google_cloudfunctions2_function.rotate_access_code.name
  
  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}

# Output l'URL de la fonction
output "rotate_access_code_url" {
  value       = google_cloudfunctions2_function.rotate_access_code.service_config[0].uri
  description = "URL de la Cloud Function de rotation du code"
}
