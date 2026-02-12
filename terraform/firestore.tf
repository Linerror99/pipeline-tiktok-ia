# Firestore Database

# Note: Firestore database doit être créé manuellement ou via gcloud
# car Terraform ne supporte pas encore la création initiale de Firestore en mode Native
# Commande: gcloud firestore databases create --location=us-central1

# Indexes Firestore (si nécessaires pour les requêtes complexes)
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
