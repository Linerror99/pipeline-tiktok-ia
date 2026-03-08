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

# ── Firestore V3 ──────────────────────────────────
variable "firestore_database_id" {
  description = "Firestore named database for V3 (separate from V2 default)"
  type        = string
  default     = "reetik-v3"
}

# ── Buckets V3 ─────────────────────────────────────
variable "bucket_artifacts_v3" {
  description = "Bucket for V3 video artifacts"
  type        = string
  default     = "reetik-v3-artifacts"
}

variable "bucket_uploads_v3" {
  description = "Bucket for V3 user uploads (files, character images)"
  type        = string
  default     = "reetik-v3-uploads"
}

variable "bucket_thumbnails_v3" {
  description = "Bucket for V3 thumbnails (Imagen 4)"
  type        = string
  default     = "reetik-v3-thumbnails"
}

# ── Cloud Functions ────────────────────────────────
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

# ── Backend ────────────────────────────────────────
variable "backend_secret_key" {
  description = "Secret key for JWT V3 token generation (minimum 32 characters)"
  type        = string
  sensitive   = true
}

variable "cors_origins" {
  description = "List of allowed CORS origins for V3"
  type        = list(string)
  default = [
    "http://localhost:5173",
    "http://localhost:3000",
  ]
}

# ── Scheduler ──────────────────────────────────────
variable "monitor_schedule" {
  description = "Cron schedule for monitor-extensions-v3 (default: every 45 seconds)"
  type        = string
  default     = "*/1 * * * *"
}

# ── Email (optionnel) ─────────────────────────────
variable "smtp_host" {
  description = "SMTP host for email notifications (optional)"
  type        = string
  default     = ""
}

variable "smtp_user" {
  description = "SMTP user"
  type        = string
  default     = ""
}

variable "smtp_password" {
  description = "SMTP password"
  type        = string
  sensitive   = true
  default     = ""
}
