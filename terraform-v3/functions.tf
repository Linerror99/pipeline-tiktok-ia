# ── Cloud Functions V3 ─────────────────────────────

# Source code archive for agent-video-veo31
data "archive_file" "agent_video_veo31" {
  type        = "zip"
  source_dir  = "${path.module}/../agent-video-veo31"
  output_path = "${path.module}/tmp/agent-video-veo31.zip"
}

resource "google_storage_bucket_object" "agent_video_veo31_source" {
  name   = "functions/agent-video-veo31-${data.archive_file.agent_video_veo31.output_md5}.zip"
  bucket = google_storage_bucket.v3_artifacts.name
  source = data.archive_file.agent_video_veo31.output_path
}

# agent-video-veo31: Cloud Storage trigger (script_v3.json upload)
resource "google_cloudfunctions2_function" "agent_video_veo31" {
  name     = "agent-video-veo31"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "generate_video_veo31"
    source {
      storage_source {
        bucket = google_storage_bucket.v3_artifacts.name
        object = google_storage_bucket_object.agent_video_veo31_source.name
      }
    }
  }

  service_config {
    max_instance_count    = 10
    available_memory      = var.cloud_functions_memory
    timeout_seconds       = var.cloud_functions_timeout
    service_account_email = google_service_account.v3_functions_sa.email
    environment_variables = {
      PROJECT_ID         = var.project_id
      FIRESTORE_DATABASE = var.firestore_database_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value     = var.bucket_artifacts_v3
    }
    retry_policy = "RETRY_POLICY_DO_NOT_RETRY"
  }

  depends_on = [google_project_service.required_apis]
}

# Source code archive for monitor-extensions-v3
data "archive_file" "monitor_extensions_v3" {
  type        = "zip"
  source_dir  = "${path.module}/../cloud-functions/monitor-extensions-v3"
  output_path = "${path.module}/tmp/monitor-extensions-v3.zip"
}

resource "google_storage_bucket_object" "monitor_extensions_v3_source" {
  name   = "functions/monitor-extensions-v3-${data.archive_file.monitor_extensions_v3.output_md5}.zip"
  bucket = google_storage_bucket.v3_artifacts.name
  source = data.archive_file.monitor_extensions_v3.output_path
}

# monitor-extensions-v3: HTTP trigger (called by Cloud Scheduler)
resource "google_cloudfunctions2_function" "monitor_extensions_v3" {
  name     = "monitor-extensions-v3"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "check_all_pending"
    source {
      storage_source {
        bucket = google_storage_bucket.v3_artifacts.name
        object = google_storage_bucket_object.monitor_extensions_v3_source.name
      }
    }
  }

  service_config {
    max_instance_count    = 3
    available_memory      = "1Gi"
    timeout_seconds       = 300
    service_account_email = google_service_account.v3_functions_sa.email
    environment_variables = {
      PROJECT_ID         = var.project_id
      FIRESTORE_DATABASE = var.firestore_database_id
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Source code archive for agent-thumbnail
data "archive_file" "agent_thumbnail" {
  type        = "zip"
  source_dir  = "${path.module}/../agent-thumbnail"
  output_path = "${path.module}/tmp/agent-thumbnail.zip"
}

resource "google_storage_bucket_object" "agent_thumbnail_source" {
  name   = "functions/agent-thumbnail-${data.archive_file.agent_thumbnail.output_md5}.zip"
  bucket = google_storage_bucket.v3_artifacts.name
  source = data.archive_file.agent_thumbnail.output_path
}

# agent-thumbnail: HTTP trigger (called by monitor-extensions-v3 on completion)
resource "google_cloudfunctions2_function" "agent_thumbnail" {
  name     = "agent-thumbnail-v3"
  location = var.region

  build_config {
    runtime     = "python312"
    entry_point = "generate_thumbnail"
    source {
      storage_source {
        bucket = google_storage_bucket.v3_artifacts.name
        object = google_storage_bucket_object.agent_thumbnail_source.name
      }
    }
  }

  service_config {
    max_instance_count    = 5
    available_memory      = "1Gi"
    timeout_seconds       = 300
    service_account_email = google_service_account.v3_functions_sa.email
    environment_variables = {
      PROJECT_ID         = var.project_id
      FIRESTORE_DATABASE = var.firestore_database_id
    }
  }

  depends_on = [google_project_service.required_apis]
}
