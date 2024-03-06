# Select the providers to be use
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.31.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.region
}
