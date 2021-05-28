terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

variable "AWSRegion" {
  type = string
  default = ""
}

provider "aws" {
  profile = "default"
  region  = var.AWSRegion
}

variable "S3BucketToScan" {
  type = string
  default = ""
}

variable "ExternalID" {
  type = string
  default = ""
}

variable "ScannerAWSAccount" {
  type = string
  default = ""
}

variable "ScannerSQSURL" {
  type = string
  default = ""
}

resource "aws_cloudformation_stack" "fss-storage-by-tf" {
  name = "fss-storage-stack-by-tf"
  capabilities = ["CAPABILITY_IAM"]

  parameters = {
    S3BucketToScan = var.S3BucketToScan,
    ScannerAWSAccount = var.ScannerAWSAccount,
    ScannerSQSURL = var.ScannerSQSURL,
    ExternalID = var.ExternalID
  }

  template_url="https://file-storage-security.s3.amazonaws.com/latest/templates/FSS-Storage-Stack.template"

}

output "CFT_STORAGE_OUTPUTS" {
  description = "Outputs from CFT"
  value       = aws_cloudformation_stack.fss-storage-by-tf.outputs
}
