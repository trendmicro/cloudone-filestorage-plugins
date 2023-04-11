# Cloud One File Storage Security Terraform Deployment

Deploy File Storage Security stacks across different cloud providers with Terraform.

## Prerequisites

1. The [Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started) (0.14.9+) is installed.
2. The [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) is installed.

## Deploy All In One Stack

- Deployment

    1. `terraform -chdir=all-in-one init`
    2. `terraform -chdir=all-in-one plan -var="AWSRegion=TheRegionOfDeployment" -var="S3BucketToScan=ProtectingBucketName" -var="ExternalID=YourExternalID"`
    3. `terraform -chdir=all-in-one apply -var="AWSRegion=TheRegionOfDeployment" -var="S3BucketToScan=ProtectingBucketName" -var="ExternalID=YourExternalID"`

- Clean Up
    - `terraform -chdir=all-in-one destroy -var="AWSRegion=TheRegionOfDeployment"`

## Deploy Scanner Stack

- Deployment
    1. `terraform -chdir=scanner-stack init`
    2. `terraform -chdir=scanner-stack plan -var="AWSRegion=TheRegionOfDeployment" -var="ExternalID=YourExternalID"`
    3. `terraform -chdir=scanner-stack apply -var="AWSRegion=TheRegionOfDeployment" -var="ExternalID=YourExternalID"`

- Clean Up
    - `terraform -chdir=scanner-stack destroy -var="AWSRegion=TheRegionOfDeployment"`

## Deploy Storage Stack

- Deployment

    1. `terraform -chdir=storage-stack init`
    2. `terraform -chdir=storage-stack plan -var="AWSRegion=TheRegionOfDeployment" -var="S3BucketToScan=ProtectingBucketName" -var="ExternalID=YourExternalID"`
    3. `terraform -chdir=storage-stack apply -var="AWSRegion=TheRegionOfDeployment" -var="S3BucketToScan=ProtectingBucketName" -var="ExternalID=YourExternalID" -var="ScannerAWSAccount=YourScannerAWSAccount" -var="ScannerSQSURL=YourScannerSQSURL"`

- Clean Up
    - `terraform -chdir=storage-stack destroy -var="AWSRegion=TheRegionOfDeployment"`
