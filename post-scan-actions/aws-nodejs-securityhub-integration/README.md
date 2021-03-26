# FSS to Security Hub Project

Pushes FSS malware detections to AWS Security Hub integration.

Change directory to `/lambda`. Run `npm run package` to install dependencies and zip it all together as `bundle.zip` and upload it to a bucket and take note of the key.
Start a new stack based on this template.

## Template Inputs

 * `snsScanResultTopicArn:`   FSS Results SNS Topic ARN
 * `LambdaZipBucket`          S3 bucket for lambda zip. If your have it under s3://bucket/path/to/zip.zip, enter 'bucket' here.
 * `LambdaZipKey`             S3 key for lambda zip. If your have it under s3://bucket/path/to/zip.zip, enter 'path/to/zip.zip' here. 