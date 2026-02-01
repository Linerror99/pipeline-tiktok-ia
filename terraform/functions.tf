# Cloud Functions (Gen 2)

# Bucket pour le code source des fonctions
resource "google_storage_bucket" "functions_source" {
  name          = "${var.project_id}-functions-source"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
  
  depends_on = [google_project_service.required_apis]
}

# === AGENT SCRIPT V2 ===
data "archive_file" "agent_script_v2_source" {
  type        = "zip"
  source_dir  = "${path.module}/../agent-script"
  output_path = "${path.module}/.terraform/tmp/agent-script-v2.zip"
}

resource "google_storage_bucket_object" "agent_script_v2_source" {
  name   = "agent-script-v2-${data.archive_file.agent_script_v2_source.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.agent_script_v2_source.output_path
}

resource "google_cloudfunctions2_function" "agent_script_v2" {
  name        = "agent-script-v2"
  location    = var.region
  description = "Parse script JSON to blocks (V2)"
  
  build_config {
    runtime     = "python312"
    entry_point = "generate_script"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.agent_script_v2_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = 10
    min_instance_count    = 0
    available_memory      = "512Mi"
    timeout_seconds       = 60
    service_account_email = google_service_account.cloud_functions_sa.email
    ingress_settings      = "ALLOW_ALL"
    
    environment_variables = {
      GCP_PROJECT        = var.project_id
      BUCKET_NAME        = google_storage_bucket.artifacts_v2.name
      AGENT_VIDEO_URL    = google_cloudfunctions2_function.agent_video_v2.service_config[0].uri
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.functions_roles
  ]
}

# IAM pour agent-script-v2 (allUsers pour invoker)
resource "google_cloudfunctions2_function_iam_member" "agent_script_v2_invoker" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.agent_script_v2.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

# === AGENT VIDEO V2 ===
data "archive_file" "agent_video_v2_source" {
  type        = "zip"
  source_dir  = "${path.module}/../agent-video"
  output_path = "${path.module}/.terraform/tmp/agent-video-v2.zip"
}

resource "google_storage_bucket_object" "agent_video_v2_source" {
  name   = "agent-video-v2-${data.archive_file.agent_video_v2_source.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.agent_video_v2_source.output_path
}

resource "google_cloudfunctions2_function" "agent_video_v2" {
  name        = "agent-video-v2"
  location    = var.region
  description = "Generate videos with Veo 3.1 (parallel generation)"
  
  build_config {
    runtime     = "python312"
    entry_point = "generate_video_v2"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.agent_video_v2_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = 10
    min_instance_count    = 0
    available_memory      = var.cloud_functions_memory
    timeout_seconds       = var.cloud_functions_timeout
    service_account_email = google_service_account.cloud_functions_sa.email
    
    environment_variables = {
      BUCKET_NAME = google_storage_bucket.artifacts_v2.name
      GCP_PROJECT = var.project_id
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.functions_roles
  ]
}

# Permettre invocations HTTP non authentifiées
resource "google_cloudfunctions2_function_iam_member" "agent_video_v2_invoker" {
  project        = google_cloudfunctions2_function.agent_video_v2.project
  location       = google_cloudfunctions2_function.agent_video_v2.location
  cloud_function = google_cloudfunctions2_function.agent_video_v2.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

# === CHECK AND RETRY CLIPS (Unified V1+V2) ===
data "archive_file" "check_retry_source" {
  type        = "zip"
  source_dir  = "${path.module}/../cloud-functions/check-and-retry-clips"
  output_path = "${path.module}/.terraform/tmp/check-and-retry-clips.zip"
}

resource "google_storage_bucket_object" "check_retry_source" {
  name   = "check-and-retry-clips-${data.archive_file.check_retry_source.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.check_retry_source.output_path
}

resource "google_cloudfunctions2_function" "check_and_retry_clips" {
  name        = "check-and-retry-clips"
  location    = var.region
  description = "Monitor and retry video operations (V1 + V2)"
  
  build_config {
    runtime     = "python312"
    entry_point = "check_and_retry_clips"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.check_retry_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = 5
    min_instance_count    = 0
    available_memory      = "1Gi"
    timeout_seconds       = var.cloud_functions_timeout
    service_account_email = google_service_account.cloud_functions_sa.email
    
    environment_variables = {
      BUCKET_NAME_V2      = google_storage_bucket.artifacts_v2.name
      AGENT_ASSEMBLER_URL = google_cloudfunctions2_function.agent_assembler_v2.service_config[0].uri
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.functions_roles
  ]
}

resource "google_cloudfunctions2_function_iam_member" "check_retry_invoker" {
  project        = google_cloudfunctions2_function.check_and_retry_clips.project
  location       = google_cloudfunctions2_function.check_and_retry_clips.location
  cloud_function = google_cloudfunctions2_function.check_and_retry_clips.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

# === AGENT ASSEMBLER V2 ===
data "archive_file" "agent_assembler_v2_source" {
  type        = "zip"
  source_dir  = "${path.module}/../agent-assembler"
  output_path = "${path.module}/.terraform/tmp/agent-assembler-v2.zip"
}

resource "google_storage_bucket_object" "agent_assembler_v2_source" {
  name   = "agent-assembler-v2-${data.archive_file.agent_assembler_v2_source.output_md5}.zip"
  bucket = google_storage_bucket.functions_source.name
  source = data.archive_file.agent_assembler_v2_source.output_path
}

resource "google_cloudfunctions2_function" "agent_assembler_v2" {
  name        = "agent-assembler-v2"
  location    = var.region
  description = "Assemble video blocks + add subtitles (V2)"
  
  build_config {
    runtime     = "python312"
    entry_point = "assemble_video"
    
    source {
      storage_source {
        bucket = google_storage_bucket.functions_source.name
        object = google_storage_bucket_object.agent_assembler_v2_source.name
      }
    }
  }
  
  service_config {
    max_instance_count    = 5
    min_instance_count    = 0
    available_memory      = "4Gi"
    timeout_seconds       = var.cloud_functions_timeout
    service_account_email = google_service_account.cloud_functions_sa.email
    
    environment_variables = {
      BUCKET_NAME_V2 = google_storage_bucket.artifacts_v2.name
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_project_iam_member.functions_roles
  ]
}

resource "google_cloudfunctions2_function_iam_member" "agent_assembler_v2_invoker" {
  project        = google_cloudfunctions2_function.agent_assembler_v2.project
  location       = google_cloudfunctions2_function.agent_assembler_v2.location
  cloud_function = google_cloudfunctions2_function.agent_assembler_v2.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}
