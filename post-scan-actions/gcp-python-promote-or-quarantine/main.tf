terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 5.11.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region = var.region
}

resource "random_id" "deploy_suffix" {
  keepers = {
    # Generate a new suffix each time we switch to a new deployment
    deployment_name = "${var.deployment_name}"
  }

  byte_length = 5
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/gcp-promote-and-quarantine-plugin.zip"
}

resource "google_service_account" "service_account" {
  account_id = "qua-pro-plugin-sa-${lower(random_id.deploy_suffix.hex)}"
  display_name = "Quarantine/Promote plugin Service Account ${random_id.deploy_suffix.hex}"
  project = var.project_id
}

resource "google_project_iam_custom_role" "promote_and_quarantine_bucket_role" {
  role_id = "plugin_storage_bucket_write_${lower(random_id.deploy_suffix.hex)}"
  title = "Promote/Quarantine Bucket Write ${random_id.deploy_suffix.hex}"
  permissions = [
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.update"
  ]
}

resource "google_project_iam_custom_role" "scanning_bucket_access_role" {
  role_id = "plugin_storage_bucket_access_${lower(random_id.deploy_suffix.hex)}"
  title = "Scanning Bucket Access ${random_id.deploy_suffix.hex}"
  permissions = var.promote_mode == "move" || var.quarantine_mode == "move" ? [
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.update"
  ] : [
    "storage.objects.get",
    "storage.objects.update"
  ]
}

resource "google_storage_bucket_iam_binding" "binding_promote_bucket" {
  count = var.promote_bucket != "" ? 1 : 0
  bucket = var.promote_bucket
  role = google_project_iam_custom_role.promote_and_quarantine_bucket_role.name
  members = [
    "serviceAccount:${google_service_account.service_account.email}",
  ]
  depends_on = [
    google_project_iam_custom_role.promote_and_quarantine_bucket_role
  ]
}

resource "google_storage_bucket_iam_binding" "binding_quarantine_bucket" {
  count = var.quarantine_bucket != "" ? 1 : 0
  bucket = var.quarantine_bucket
  role = google_project_iam_custom_role.promote_and_quarantine_bucket_role.name
  members = [
    "serviceAccount:${google_service_account.service_account.email}",
  ]
  depends_on = [
    google_project_iam_custom_role.promote_and_quarantine_bucket_role
  ]
}

resource "google_storage_bucket_iam_binding" "binding_scanning_bucket" {
  bucket = var.scanning_bucket
  role = google_project_iam_custom_role.scanning_bucket_access_role.name
  members = [
    "serviceAccount:${google_service_account.service_account.email}",
  ]
  depends_on = [
    google_project_iam_custom_role.scanning_bucket_access_role
  ]
}

resource "google_storage_bucket" "artifacts_bucket" {
  name = "artifacts-promote-and-quarantine-plugin-${lower(random_id.deploy_suffix.hex)}"
  location = var.region
  project = var.project_id
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket_object" "archive" {
  name   = "gcp-promote-and-quarantine-plugin.zip"
  bucket = google_storage_bucket.artifacts_bucket.name
  source = data.archive_file.source.output_path
  content_type = "application/zip"

  depends_on   = [
    google_storage_bucket.artifacts_bucket,
    data.archive_file.source
  ]
}

resource "google_cloudfunctions_function" "promote_and_quarantining_plugin" {
  name = "${var.plugin_prefix}-promote-and-quarantine-${random_id.deploy_suffix.hex}"
  description = "Promote and Quarantine plugin ${random_id.deploy_suffix.hex}"
  source_archive_bucket = google_storage_bucket.artifacts_bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  runtime = "python38"
  entry_point = "main"
  project = var.project_id

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource = "projects/${var.project_id}/topics/${var.scan_result_topic}"
  }

  environment_variables = {
    QUARANTINE_STORAGE_BUCKET = var.quarantine_bucket
    QUARANTINE_MODE = var.quarantine_mode
    PROMOTE_STORAGE_BUCKET = var.promote_bucket
    PROMOTE_MODE = var.promote_mode
  }

  service_account_email = google_service_account.service_account.email

  depends_on = [
    google_storage_bucket.artifacts_bucket,
    google_storage_bucket_object.archive
  ]
}
