variable "deployment_name" {
  type        = string
  description = "The name of the deployment. This is used to generate unique suffix for some resource."
}

variable "project_id" {
  type        = string
  description = "ID of the GCP project which the plugin will be deployed."
  sensitive   = true
}

variable "region" {
  type        = string
  description = "GCP region to deploy the plugin."
}

variable "scanner_pubsub_topic_project" {
  type        = string
  description = "GCP project ID of the scanner pubsub topic."
  sensitive   = true
}

variable "scanner_pubsub_topic" {
  type        = string
  description = "Pub/Sub topic to trigger scanner."
}

variable "scan_result_topic" {
  type        = string
  description = "Scan result Pub/Sub topic."
}

variable "scanning_bucket_name" {
  type        = string
  description = "Name of the GCS bucket to store scanned files."
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

variable "trend_micro_fss_bucket_listener_role_id" {
  type        = string
  description = "ID of the bucket listener role. This is used to sign presigned URL."
}
