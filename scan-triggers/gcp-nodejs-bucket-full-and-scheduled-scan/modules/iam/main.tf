resource "google_service_account" "service_account" {
  account_id   = var.id
  display_name = var.name
  description  = var.description
}

resource "google_project_iam_member" "role_binding" {
  for_each = var.roles
  project  = each.value["project"]
  role     = each.value["name"]
  member   = google_service_account.service_account.member
}
