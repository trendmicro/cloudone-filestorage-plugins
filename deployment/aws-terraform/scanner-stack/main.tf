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

variable "ExternalID" {
  type = string
  default = ""
}

resource "aws_cloudformation_stack" "fss-scanner-by-tf" {
  name = "fss-scanner-stack-by-tf"
  capabilities = ["CAPABILITY_IAM"]

  parameters = {
    ExternalID = var.ExternalID
  }

  template_url="https://file-storage-security.s3.amazonaws.com/latest/templates/FSS-Scanner-Stack.template"

}

output "CFT_STORAGE_OUTPUTS" {
  description = "Outputs from CFT"
  value       = aws_cloudformation_stack.fss-scanner-by-tf.outputs
}
