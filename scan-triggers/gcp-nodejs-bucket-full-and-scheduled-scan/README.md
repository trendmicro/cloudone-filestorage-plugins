# Cloud One File Storage Security Scan Trigger - GCP Full Scan and Scheduled Scan

This plugin is design to perform full scan and schedule scan on GCP cloud storage.

## Prerequest

1. Install File storage security in you GCP environment
1. [Terraform](https://developer.hashicorp.com/terraform/install) (Not needed for cloud shell.)

## Installation

### Using GCP Cloud Shell

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Ftrendmicro%2Fcloudone-filestorage-plugins&cloudshell_workspace=scan-triggers%2Fgcp-nodejs-bucket-full-and-scheduled-scan&cloudshell_tutorial=docs%2Ftutorial.md)

### Local machine

1. Initialize terraform

   ```bash
   terraform init
   ```

1. Deploy the function and fill the variables following the CLI. (Or using the `main.auto.tfvars` file)

   ```sh
   terraform apply
   ```

   Instead of filling in the variables individually, you can create and use a `main.auto.tfvars` file. Enter the variables in to the `main.auto.tfvars.example` file, and then save the file as `main.auto.tfvars`. Once you have created and saved the file, you can reuse the file rather than fill in the variables every time.

1. Remember to save the `terraform.tfstate` file.

### Variables

- **deployment_name**: Name of the deployment. This is used to generate unique suffix for resources created by the plugin.
- **project_id**: GCP project ID which the plugin will be deployed.
- **region**: GCP region to deploy the plugin.
- **scanner_pubsub_topic_project**: GCP project ID which the scanner Pub/Sub topic is deployed. This value can be found in the FSS scanner deploy output **scannerProjectID**.
- **scanner_pubsub_topic**: Scanner Pub/Sub topic name. This value can be found in the FSS scanner deployment output **scannerTopic**.
- **scan_result_topic**: Scan result Pub/Sub topic name. This value can be found in the FSS storage deployment output **scanResultTopic**.
- **scanning_bucket_name**: GCS bucket to perform schedule scan on.
- **schedular_settings**: Settings for the cloud scheduler trigger for workflow. Default to run on every monday at 12:00 AM UTC.
- **trend_micro_fss_bucket_listener_role_id**: Reused custom role used by the bucketListener function to create presigned URL. This value can be found in IAM console page with title `trend-micro-fss-bucket-listener-role`.

## Test plugin

1. Find the deployed workflow. Workflow name can be found in the terraform output **workflow_name**.

1. Execute workflow using the following argument.

   ```json
   { "bucketName": "<SCANNING_BUCKET_NAME>" }
   ```
