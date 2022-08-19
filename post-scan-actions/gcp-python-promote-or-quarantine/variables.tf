variable "project_id" {
  type = string
  description = "ID of the GCP project which the plugin will be deployed"
  sensitive = true
}

variable "region" {
  type = string
  description = "GCP region to deploy the plugin"
}

variable "plugin_prefix" {
  type = string
  description = "GCP function prefix to use for the plugin"
}

variable "deployment_name" {
  type = string
  description = "The name of the deployment"
}

variable "scan_result_topic" {
  type = string
  description = "The name of the Pub/Sub topic for scan results topic"
}

variable "scanning_bucket" {
  type = string
  description = "Scanning bucket name"
  nullable = false
}

variable "quarantine_mode" {
  type = string
  description = "The quarantine mode to use: 'move' or 'copy'"
  nullable = false
  validation {
    condition = contains(["move", "copy"], var.quarantine_mode)
    error_message = "Value must be one of 'move' or 'copy'."
  }
}

variable "quarantine_bucket" {
  type = string
  description = "The quarantine bucket to use. Leave it empty if you don't want to quarantine files."
}

variable "promote_mode" {
  type = string
  description = "The promote mode to use: 'move' or 'copy'"
  nullable = false
  validation {
    condition = contains(["move", "copy"], var.promote_mode)
    error_message = "Value must be one of 'move' or 'copy'."
  }
}

variable "promote_bucket" {
  type = string
  description = "The promote bucket to use. Leave it empty if you don't want to promote files."
}
