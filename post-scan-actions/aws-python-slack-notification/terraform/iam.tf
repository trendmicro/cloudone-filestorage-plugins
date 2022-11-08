# Lambda execution policy for the IAM role
data "aws_iam_policy_document" "SlackNotificationLambdaPolicy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]

    }
  }
}

# Lambda execution role
resource "aws_iam_role" "SlackNotificationLambdaRole" {
  name_prefix   = "SlackNotificationLambdaRole-"
  description = "AWS IAM Role for managing aws lambda"
  assume_role_policy = data.aws_iam_policy_document.SlackNotificationLambdaPolicy.json
}
