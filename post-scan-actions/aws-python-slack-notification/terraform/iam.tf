# Lambda execution role
resource "aws_iam_role" "SlackNotificationLambdaRole" {
  name_prefix   = "SlackNotificationLambdaRole-"
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