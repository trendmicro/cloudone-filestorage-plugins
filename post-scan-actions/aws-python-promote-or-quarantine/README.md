# Post Scan Action - Promote or Quarantine

This example Lambda function promotes clean files and quarantines malicious ones scanned by Cloud One File Storage Security.

## Prerequisites

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- Two S3 buckets: a 'Promote bucket' for clean files, and a 'Quarantine bucket' for quarantined files
- An IAM role for this Lambda function that has:
  - `AWSLambdaBasicExecutionRole` policy
  - Permission to copy objects from the S3 bucket scanned by File Storage Security into the Promote or Quarantine buckets

    Example IAM Policy

     ```json
     {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Sid": "CopyFromScanningBucket",
                 "Effect": "Allow",
                 "Action": [
                     "s3:GetObject",
                     "s3:DeleteObject",
                     "s3:GetObjectTagging"
                 ],
                 "Resource": "arn:aws:s3:::<YOUR_BUCKET_TO_SCAN>/*"
             },
             {
                 "Sid": "CopyToPromoteOrQuarantineBucket",
                 "Effect": "Allow",
                 "Action": [
                     "s3:PutObject",
                     "s3:PutObjectTagging"
                 ],
                 "Resource": [
                     "arn:aws:s3:::<YOUR_QUARANTINE_BUCKET>/*",
                     "arn:aws:s3:::<YOUR_PROMOTE_BUCKET>/*"
                 ]
             }
         ]
     }
     ```

## Deploy

```bash
FUNCTION_NAME=<YOUR_FUNC_NAME> ROLE_ARN=<YOUR_ROLE_ARN> \
PROMOTE_BUCKET=<YOUR_PROMOTE_BUCKET_NAME> QUARANTINE_BUCKET=<YOUR_QUARANTINE_BUCKET_NAME> \
make create-function
```
