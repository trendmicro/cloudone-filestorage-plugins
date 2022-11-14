# Configure the variables here
variable "region" {
  type = string
  description = "AWS region"
  default = "us-east-1"
  validation {
    condition     = can(regex("[a-z][a-z]-[a-z]+-[1-2]", var.region))
    error_message = "Must be valid AWS Region names."
  }
}

variable "scan_result_topic_arn" {
  type = string
  default = ""
  description = "The ARN of the scan result SNS topic in storage stack."
}

variable "slack_webhook_url" {
  type = string
  default = ""
  description = "The URL of the Slack Webhook."
}

variable "slack_channel" {
  type = string
  default = ""
  description = "The name of the Slack channel."
}

variable "slack_username" {
  type = string
  default = "FSS-Notification"
  description = "The username of the Slack notification."
}
