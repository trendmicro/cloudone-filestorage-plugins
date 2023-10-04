# FSS to Security Hub Project

Pushes FSS malware detections to AWS Security Hub integration.

Change directory to `/lambda`. Run `npm run package` to install dependencies and zip it all together as `bundle.zip` and upload it to a bucket and take note of the key.
Start a new stack based on this template.

## What is AWS Security Hub?
AWS Security Hub provides a comprehensive view of your security posture in Amazon Web Services (AWS) and helps you check your environment against security standards and Malicious file detection using serverless plugin.
    In order to push malware finding to AWS Security hub, open source serverless plugin need to be deployed and configured with AWS SNS topic created by Scanner Stack created in previous step.

## Deployment steps
1.	Visit plugin from serverless application repository
 
2.	Enter AWS Account details and AWS Security hub ARN
AWSACCOUNTNO: Provide your aws account ID
AWSSecurityHubARN: arn:aws:securityhub:<region>:<aws acc no>:product/<aws acc no>/default


3.	Copy ScanResultTopicArn from scanner cloudformation stack output. This is the same ARN that we have used in previous step for Quarantine and promote object.

 
4.	Enter ScanResultTopicARN to serverless application parameter and proceed to Deploy
 

5.	Verify serverless plugin deployment is completed.
 

## Cloudformation Template Inputs

 * `snsScanResultTopicArn:`   FSS Results SNS Topic ARN
 * `LambdaZipBucket`          S3 bucket for lambda zip. If your have it under s3://bucket/path/to/zip.zip, enter 'bucket' here.
 * `LambdaZipKey`             S3 key for lambda zip. If your have it under s3://bucket/path/to/zip.zip, enter 'path/to/zip.zip' here. 
