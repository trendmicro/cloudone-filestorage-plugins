# Lambda execution policy for ScanningBucketNamePolicy
resource "aws_iam_policy" "scanning_bucket_name_policy" {
  name_prefix = "ScanningBucketNamePolicy-"
  description  = "AWS IAM Policy for managing aws lambda role"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:GetObjectTagging"
      ],
      "Resource": "arn:aws:s3:::${var.ScanningBucketName}/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::${var.ScanningBucketName}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectTagging",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        %{ if local.promote_enalbed }"arn:aws:s3:::${var.PromoteBucketName}/*"%{ else }%{ endif }
        %{ if local.promote_enalbed && local.quaratine_enalbed },%{ else }%{ endif }
        %{ if local.quaratine_enalbed }"arn:aws:s3:::${var.QuarantineBucketName}/*"%{ else }%{ endif }
        "arn:aws:s3:::${var.QuarantineBucketName}/*"
      ]
    }
  ]
}
EOF
}

# Lambda execution role
resource "aws_iam_role" "PromoteOrQuarantineLambdaRole" {
  name_prefix   = "PromoteOrQuarantineLambdaRole-"
  description = "AWS IAM Role for managing aws lambda"
  assume_role_policy = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

# Attach the policy ScanningBucketNamePolicy to the role
resource "aws_iam_role_policy_attachment" "ScanningBucketNamePolicyAttachment" {
  depends_on = [aws_iam_role.PromoteOrQuarantineLambdaRole]
  role = aws_iam_role.PromoteOrQuarantineLambdaRole.name
  policy_arn = aws_iam_policy.ScanningBucketNamePolicy.arn
}
