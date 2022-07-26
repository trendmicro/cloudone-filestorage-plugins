# Cloud One File Storage Security Post Scan Action for GCP - Promote or Quarantine

## Overview

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

This tutorial will guide you to deploy a promote and quarantine function.

## Project Setup

Copy the execute the script below to select the project where the storage stack is deployed.

<walkthrough-project-setup></walkthrough-project-setup>

```sh
gcloud config set project <walkthrough-project-id/>
```

## Deploy promote and quarantine function

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
