output "backend_v3_url" {
  description = "URL of the Backend V3 Cloud Run service"
  value       = google_cloud_run_v2_service.backend_v3.uri
}

output "agent_video_veo31_url" {
  description = "URL of the agent-video-veo31 Cloud Function"
  value       = google_cloudfunctions2_function.agent_video_veo31.service_config[0].uri
}

output "monitor_extensions_v3_url" {
  description = "URL of the monitor-extensions-v3 Cloud Function"
  value       = google_cloudfunctions2_function.monitor_extensions_v3.service_config[0].uri
}

output "agent_thumbnail_url" {
  description = "URL of the agent-thumbnail Cloud Function"
  value       = google_cloudfunctions2_function.agent_thumbnail.service_config[0].uri
}

output "bucket_artifacts_v3" {
  description = "V3 artifacts bucket name"
  value       = google_storage_bucket.v3_artifacts.name
}

output "bucket_uploads_v3" {
  description = "V3 uploads bucket name"
  value       = google_storage_bucket.v3_uploads.name
}

output "bucket_thumbnails_v3" {
  description = "V3 thumbnails bucket name"
  value       = google_storage_bucket.v3_thumbnails.name
}

output "artifact_registry_v3" {
  description = "V3 Artifact Registry repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.v3_repo.repository_id}"
}
