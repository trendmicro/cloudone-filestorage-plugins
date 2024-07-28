variable "project_id" {
  type        = string
  description = "ID of the GCP project which the plugin will be deployed."
  sensitive   = true
}

variable "region" {
  type        = string
  description = "GCP region to deploy the plugin."
}

variable "service_account" {
  type        = string
  description = "The service account to use execute the workflow."
}

variable "schedular_settings" {
  type = object({
    cron     = string
    timezone = string
  })
  description = "Settings for the cloud scheduler trigger for workflow. Default to run on every monday at 12:00 AM UTC."
  default = {
    cron     = "0 0 * * 1",
    timezone = "Etc/UTC"
  }
}

variable "scanning_bucket_name" {
  type        = string
  description = "Name of the GCS bucket to store scanned files."
}

variable "scan_trigger_function_url" {
  type = string
  description = "URL of the function to trigger scan."
}

variable "suffix" {
  type = string
  description = "Suffix to append to the resources."
}
