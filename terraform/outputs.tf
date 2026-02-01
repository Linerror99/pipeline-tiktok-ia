output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "bucket_v1_name" {
  description = "V1 Artifacts Bucket Name"
  value       = google_storage_bucket.artifacts_v1.name
}

output "bucket_v2_name" {
  description = "V2 Artifacts Bucket Name"
  value       = google_storage_bucket.artifacts_v2.name
}

output "agent_script_v2_url" {
  description = "Agent Script V2 Function URL"
  value       = google_cloudfunctions2_function.agent_script_v2.service_config[0].uri
}

output "agent_video_v2_url" {
  description = "Agent Video V2 Function URL"
  value       = google_cloudfunctions2_function.agent_video_v2.service_config[0].uri
}

output "check_and_retry_url" {
  description = "Check and Retry Function URL"
  value       = google_cloudfunctions2_function.check_and_retry_clips.service_config[0].uri
}

output "agent_assembler_v2_url" {
  description = "Agent Assembler V2 Function URL"
  value       = google_cloudfunctions2_function.agent_assembler_v2.service_config[0].uri
}

output "service_account_email" {
  description = "Service Account Email"
  value       = google_service_account.cloud_functions_sa.email
}

output "scheduler_job_name" {
  description = "Cloud Scheduler Job Name"
  value       = google_cloud_scheduler_job.check_and_retry.name
}
