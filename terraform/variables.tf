variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "prod"
}

variable "bucket_name_v1" {
  description = "Bucket name for V1 artifacts"
  type        = string
}

variable "bucket_name_v2" {
  description = "Bucket name for V2 artifacts"
  type        = string
}

variable "cloud_functions_timeout" {
  description = "Timeout for Cloud Functions in seconds"
  type        = number
  default     = 540
}

variable "cloud_functions_memory" {
  description = "Memory allocation for Cloud Functions"
  type        = string
  default     = "2Gi"
}
