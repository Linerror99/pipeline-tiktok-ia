# ── Firestore Indexes V3 ───────────────────────────

# V3 utilise une base Firestore nommée "reetik-v3", séparée de la base
# "(default)" de V2. Cela évite tout conflit de données entre versions.
# Collections V3: users_v3, projects, characters, scenarios, videos_v3, v3_veo_operations.

resource "google_firestore_index" "projects_by_user" {
  project    = var.project_id
  database   = google_firestore_database.v3_db.name
  collection = "projects"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "characters_by_project" {
  project    = var.project_id
  database   = google_firestore_database.v3_db.name
  collection = "characters"

  fields {
    field_path = "project_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "scenarios_by_project" {
  project    = var.project_id
  database   = google_firestore_database.v3_db.name
  collection = "scenarios"

  fields {
    field_path = "project_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "videos_v3_by_user" {
  project    = var.project_id
  database   = google_firestore_database.v3_db.name
  collection = "videos_v3"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "videos_v3_by_project" {
  project    = var.project_id
  database   = google_firestore_database.v3_db.name
  collection = "videos_v3"

  fields {
    field_path = "project_id"
    order      = "ASCENDING"
  }
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "veo_operations_pending" {
  project    = var.project_id
  database   = google_firestore_database.v3_db.name
  collection = "v3_veo_operations"

  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  fields {
    field_path = "updated_at"
    order      = "ASCENDING"
  }
}
