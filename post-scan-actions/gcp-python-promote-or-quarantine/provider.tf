terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.11.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google" {
  alias   = "quarantine_provider"
  project = var.quarantine_bucket_properties.project_id != "" ? var.quarantine_bucket_properties.project_id : var.project_id
  region  = var.quarantine_bucket_properties.region != "" ? var.quarantine_bucket_properties.region : var.region
}

provider "google" {
  alias   = "promote_provider"
  project = var.promote_bucket_properties.project_id != "" ? var.promote_bucket_properties.project_id : var.project_id
  region  = var.promote_bucket_properties.region != "" ? var.promote_bucket_properties.region : var.region
}
