variable "project_id" {
  type        = string
  description = "ID of the GCP project which the plugin will be deployed."
  sensitive   = true
}

variable "region" {
  type        = string
  description = "GCP region to deploy the plugin."
}

variable "service_account_email" {
  type        = string
  description = "Email of the service account which cloud function will used."
}

variable "scanner_pubsub_topic" {
  type        = string
  description = "Pub/Sub topic to trigger scanner."
}

variable "scanner_pubsub_topic_project" {
  type        = string
  description = "Scanner Pub/Sub topic gcp project."
}

variable "scan_result_topic" {
  type        = string
  description = "Scan result Pub/Sub topic."
}

variable "deployment_name" {
  type        = string
  description = "The name of the deployment. This is used to generate unique suffix for some resource."
}

variable "report_object_key" {
  type        = bool
  default     = false
  description = "If true, the report object key will be used instead of sha256."
}

variable "suffix" {
  type        = string
  description = "Suffix to be appended to the resources."
}
