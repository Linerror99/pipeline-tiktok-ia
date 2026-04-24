# Cloud Functions V2 supprimées (rotate-access-code retiré — non utilisé en V3).
# Le bucket function_source est conservé si d'autres fonctions en auraient besoin.
resource "google_storage_bucket" "function_source" {
  name                        = "${var.project_id}-function-source"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}
