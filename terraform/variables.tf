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

variable "bucket_name_v2" {
  description = "Bucket name for V2 artifacts (Veo 3.1)"
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

variable "backend_secret_key" {
  description = "Secret key for JWT token generation (minimum 32 characters)"
  type        = string
  sensitive   = true
}

variable "cors_origins" {
  description = "List of allowed CORS origins"
  type        = list(string)
  default     = []
}
