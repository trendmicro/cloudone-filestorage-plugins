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

variable "scanning_bucket_name" {
  type = string
  default = ""
  description = "The S3 bucket scanned by Trend Micro Cloud One File Storage Security."
 }

variable "scan_result_topic_arn" {
  type = string
  default = ""
  description = "The ARN of the scan result SNS topic in storage stack."
 }

variable "promote_bucket_name" {
  type = string
  default = ""
  description = "[Optional] The bucket name used to promote files without malicious intent. Leave the bucket name blank to disable promoting."
 }

variable "promote_mode" {
  type = string
  description = "The method by which files were promoted. (Options: move, copy)"
  default = "move"
  validation {
    condition = contains(["move", "copy"], var.PromoteMode)
    error_message = "The promote mode must be either move or copy."
  }
 }

variable "quarantine_bucket_name" {
  type = string
  default = ""
  description = "[Optional] The bucket name to quarantine malicious files. Leave the bucket name blank to disable quarantining"
 }

 variable "quarantine_mode" {
  type = string
  description = "The method by which files were quarantined. (Options: move, copy)"
  default = "move"
  validation {
    condition = contains(["move", "copy"], var.QuarantineMode)
    error_message = "The quarantine mode must be either move or copy."
  }
 }

variable "acl" {
  type = string
  default = ""
  description = "[Optional] Apply an access control list (ACL) on the file after it has been promoted or quarantined. (Options: private, public-read, public-read-write, authenticated-read, aws-exec-read, bucket-owner-read, bucket-owner-full-control)"
  validation {
    condition = contains(["private, public-read", "public-read-write", "authenticated-read", "aws-exec-read", "bucket-owner-read", "bucket-owner-full-control"], var.acl)
    error_message = "The ACL is not valid"
  }
 }
