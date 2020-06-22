# Post Scan Action - Promote or Quarantine

The Lambda Function example to promote clean files or quarantine malicious files scanned by Cloud One File Storage Security

## Prerequisite

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- Two S3 Buckets, one for promote and one for quarantine.
- An IAM role for this Lambda Function that has
  - `AWSLambdaBasicExecutionRole` policy
  - Permission to copy objects from S3 Bucket scanned by File Storage Security into Promote or Quarantine S3 Bucket

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
                     "s3:DeleteObject"
                 ],
                 "Resource": "arn:aws:s3:::<YOUR_BUCKET_TO_SCAN>/*"
             },
             {
                 "Sid": "CopyToPromoteOrQuarantineBucket",
                 "Effect": "Allow",
                 "Action": "s3:PutObject",
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
