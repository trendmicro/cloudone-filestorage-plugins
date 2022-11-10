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

variable "ScanResultTopicARN" {
  type = string
  default = ""
  description = "The ARN of the scan result SNS topic in storage stack."
}

variable "SlackWebhookURL" {
  type = string
  default = ""
  description = "The URL of the Slack Webhook."
}

variable "SlackChannel" {
  type = string
  default = ""
  description = "The name of the Slack channel."
}

variable "SlackUsername" {
  type = string
  default = "FSS-Notification"
  description = "The username of the Slack notification."
}
