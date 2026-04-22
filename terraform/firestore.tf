# Firestore Database V3 (séparée de la (default) utilisée par V2)
resource "google_firestore_database" "reetik_v3" {
  project     = var.project_id
  name        = "reetik-v3"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.required_apis]
}

# ── Indexes V3 ─────────────────────────────────────────────────────────────

resource "google_firestore_index" "v3_videos_status_index" {
  project    = var.project_id
  database   = google_firestore_database.reetik_v3.name
  collection = "videos_v3"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "v3_projects_user_index" {
  project    = var.project_id
  database   = google_firestore_database.reetik_v3.name
  collection = "projects_v3"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# ── Indexes V2 (base (default)) ────────────────────────────────────────────

# Note: Firestore database doit être créé manuellement ou via gcloud
# car Terraform ne supporte pas encore la création initiale de Firestore en mode Native
# Commande: gcloud firestore databases create --location=us-central1

resource "google_firestore_index" "video_status_index" {
  collection = "video_status"
  
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_firestore_index" "v2_veo_operations_index" {
  collection = "v2_veo_operations"
  
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_firestore_index" "video_operations_index" {
  collection = "video_operations"
  
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "retry_count"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "updated_at"
    order      = "DESCENDING"
  }
  
  depends_on = [google_project_service.required_apis]
}
