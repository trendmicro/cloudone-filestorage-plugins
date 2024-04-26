locals {
  source_files = [
    "${path.root}/src/index.js",
    "${path.root}/package.json",
    "${path.root}/yarn.lock"
  ]
  project = var.project_id
}

resource "google_storage_bucket" "function_artifact_bucket" {
  name                        = "tmfss-fullscan-artifact"
  location                    = var.region
  uniform_bucket_level_access = true
}

data "archive_file" "function_artifact" {
  type        = "zip"
  output_path = "${path.root}/artifact.zip"
  source {
    content  = file(local.source_files[0])
    filename = "src/${basename(local.source_files[0])}"
  }

  source {
    content  = file(local.source_files[1])
    filename = basename(local.source_files[1])
  }

  source {
    content  = file(local.source_files[2])
    filename = basename(local.source_files[2])
  }
}

resource "google_storage_bucket" "bucket" {
  name                        = "${local.project}-gcf-source-${var.suffix}" # Every bucket name must be globally unique
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "object" {
  name   = "artifact.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.function_artifact.output_path
}

resource "google_cloudfunctions2_function" "function" {
  name        = "tmfss-fs-pl-st-${var.suffix}"
  location    = var.region
  description = "TM C1 FSS Fullscan and schedule scan scan trigger function"

  build_config {
    runtime     = "nodejs20"
    entry_point = "handler"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    service_account_email = var.service_account_email
    environment_variables = {
      "SCANNER_PUBSUB_TOPIC" : var.scanner_pubsub_topic
      "SCANNER_PROJECT_ID" : var.scanner_pubsub_topic_project
      "SCAN_RESULT_TOPIC" : var.scan_result_topic
      "DEPLOYMENT_NAME" : var.deployment_name
      "REPORT_OBJECT_KEY" : var.report_object_key
    }
  }
}
