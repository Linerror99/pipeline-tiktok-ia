terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── APIs requises ──────────────────────────────────
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
    "monitoring.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

# ── Service Account V3 ────────────────────────────
resource "google_service_account" "v3_functions_sa" {
  account_id   = "reetik-v3-functions"
  display_name = "Reetik V3 Cloud Functions Service Account"
  depends_on   = [google_project_service.required_apis]
}

# ── Firestore Database V3 (séparée de la base "(default)" de V2) ──
resource "google_firestore_database" "v3_db" {
  project     = var.project_id
  name        = var.firestore_database_id
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  depends_on  = [google_project_service.required_apis]
}

resource "google_project_iam_member" "v3_functions_roles" {
  for_each = toset([
    "roles/storage.objectAdmin",
    "roles/datastore.user",
    "roles/cloudfunctions.invoker",
    "roles/aiplatform.user",
    "roles/logging.logWriter",
    "roles/run.invoker",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.v3_functions_sa.email}"
}
