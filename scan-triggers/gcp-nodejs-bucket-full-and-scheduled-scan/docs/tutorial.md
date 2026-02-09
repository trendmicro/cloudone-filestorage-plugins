# Cloud One File Storage Security Full scan and schedule scan plugin for GCP

## Overview

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

This tutorial will guide you to deploy the full scan and schedule scan plugin.

## Project Setup

Copy the execute the script below to select the project where the storage stack is deployed.

<walkthrough-project-setup></walkthrough-project-setup>

```sh
gcloud config set project <walkthrough-project-id/>
```

## Deploy full scan and schedule scan plugin

1. Initialize terraform.

   ```sh
   terraform init
   ```

1. Deploy the resources and fill the variables following the CLI. (Or using the `main.auto.tfvars` file)

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
