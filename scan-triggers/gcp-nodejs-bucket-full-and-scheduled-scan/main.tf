locals {
  services = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
    "cloudtasks.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
    "workflows.googleapis.com",
  ]
}

resource "google_project_service" "enable_apis" {
  for_each           = toset(local.services)
  service            = each.value
  disable_on_destroy = false
}

resource "random_id" "deploy_suffix" {
  keepers = {
    # Generate a new suffix each time we switch to a new deployment
    deployment_name = "${var.deployment_name}"
  }

  byte_length = 3
}

resource "google_project_iam_custom_role" "workflow_custom_role" {
  role_id = "tmfssfsplwf${lower(random_id.deploy_suffix.hex)}"
  title   = "TM C1FSS fullscan and schedule scan workflow custom role"
  permissions = [
    "iam.serviceAccounts.actAs"
  ]
  project = var.project_id
}

module "function_sa" {
  source = "./modules/iam"
  id     = "tmfss-st-sa${lower(random_id.deploy_suffix.hex)}"
  name   = "tmfss-st-sa"
  roles = {
    readObejctRole = {
      name    = "roles/storage.objectViewer"
      project = var.project_id
    }
    messagePublishRole = {
      name    = "roles/pubsub.publisher"
      project = var.scanner_pubsub_topic_project
    }
    signObjectRole = {
      name    = var.trend_micro_fss_bucket_listener_role_id
      project = var.project_id
    }
  }
  description = "Service account for C1FSS fullscan and schedule scan plugin cloud function"
}

module "workflow_sa" {
  source = "./modules/iam"
  id     = "tmfss-wf-sa-${lower(random_id.deploy_suffix.hex)}"
  name   = "tmfss-wf-sa"
  roles = {
    listObjectsRole = {
      name    = "roles/storage.objectViewer"
      project = var.project_id
    }
    functionTriggerRole = {
      name    = "roles/run.invoker"
      project = var.project_id
    }
    workflowTriggerRole = {
      name    = "roles/workflows.invoker"
      project = var.project_id
    }
    cloudTaskCreateRole = {
      name    = "roles/cloudtasks.enqueuer"
      project = var.project_id
    }
    customRole = {
      name    = google_project_iam_custom_role.workflow_custom_role.name
      project = var.project_id
    }
  }
  description = "Service account for C1FSS fullscan and schedule scan plugin workflow"
  depends_on  = [module.function_sa]
}

module "function" {
  source                       = "./modules/cloudfunctions"
  service_account_email        = module.function_sa.service_account_email
  deployment_name              = var.deployment_name
  project_id                   = var.project_id
  region                       = var.region
  scan_result_topic            = var.scan_result_topic
  scanner_pubsub_topic_project = var.scanner_pubsub_topic_project
  scanner_pubsub_topic         = var.scanner_pubsub_topic
  suffix                       = lower(random_id.deploy_suffix.hex)
}

module "workflow" {
  source                    = "./modules/workflow"
  project_id                = var.project_id
  region                    = var.region
  service_account           = module.workflow_sa.service_account_email
  schedular_settings        = var.schedular_settings
  scanning_bucket_name      = var.scanning_bucket_name
  scan_trigger_function_url = module.function.cloudfunction_url
  suffix                    = lower(random_id.deploy_suffix.hex)
}
