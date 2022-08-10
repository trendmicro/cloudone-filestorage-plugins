# Cloud One File Storage Security Post Scan Action for GCP - Promote or Quarantine

## Prerequisites

1. **Install supporting tools**
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk)
   - [Terraform](https://www.terraform.io/downloads)

## Installation

### With GCP Cloud Shell

1. Visit [![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Ftrendmicro%2Fcloudone-filestorage-plugins.git&cloudshell_workspace=post-scan-actions%2Fgcp-python-promote-or-quarantine&cloudshell_tutorial=docs/deploy-tutorial.md)

### LocalMachine

1. Login to the Google cloud SDK

   ```sh
   gcloud init
   ```

1. Create a function zip for the deployment using make.

   ```sh
   make
   ```

1. Initialize terraform.

   ```sh
   terraform init
   ```

1. Deploy the function and fill the variables following the CLI. (Or using the `main.auto.tfvars` file)

   ```sh
   terraform apply
   ```

   Instead of filling in the variables individually, you can create and use a `main.auto.tfvars` file. Enter the variables in to the `main.auto.tfvars.example` file, and then save the file as `main.auto.tfvars`. Once you have created and saved the file, you can reuse the file rather than fill in the variables every time.
