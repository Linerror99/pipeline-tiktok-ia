terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  # Backend pour stocker l'état Terraform (optionnel mais recommandé)
  # backend "gcs" {
  #   bucket = "votre-bucket-tfstate"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Activer les APIs nécessaires
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "cloudbuild.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
    "artifactregistry.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com"
  ])
  
  service            = each.key
  disable_on_destroy = false
}

# Service Account pour Cloud Functions
resource "google_service_account" "cloud_functions_sa" {
  account_id   = "pipeline-tiktok-functions"
  display_name = "Service Account for TikTok Pipeline Cloud Functions"
  
  depends_on = [google_project_service.required_apis]
}

# IAM roles pour le service account
resource "google_project_iam_member" "functions_roles" {
  for_each = toset([
    "roles/storage.objectAdmin",
    "roles/datastore.user",
    "roles/cloudfunctions.invoker",
    "roles/aiplatform.user",
    "roles/logging.logWriter"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.cloud_functions_sa.email}"
}
