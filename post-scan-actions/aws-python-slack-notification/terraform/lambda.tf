# Zip the lambda code
data "archive_file" "zip_the_python_code" {
  type        = "zip"
  source_file = "../handler.py"
  output_path = "${path.module}/lambda_zip/handler.zip"
}

# Create the lambda function
resource "aws_lambda_function" "slack_notification_lambda" {
  filename      = "${path.module}/lambda_zip/handler.zip"
  function_name = "SlackNotificationLambda"
  role          = aws_iam_role.slack_notification_lambda_role.arn
  handler       = "handler.lambda_handler"
  memory_size = 512
  timeout = 30
  runtime = "python3.8"
  tracing_config {
      mode = "Active"
    }
  environment {
    variables = {
      SLACK_URL= var.slack_webhook_url
      SLACK_CHANNEL= var.slack_channel
      SLACK_USERNAME= var.slack_username
    }
  }
}

# Allows Lambda to add a trigger to SNS
resource "aws_lambda_permission" "slack_notification_lambda_permission" {
  statement_id = "AllowExecutionFromSNS"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.slack_notification_lambda.arn}"
  principal = "sns.amazonaws.com"
  source_arn = "${var.scan_result_topic_arn}"
}

# Create the sns event source mapping to lambda
resource "aws_sns_topic_subscription" "scan_result" {
  depends_on = [aws_lambda_function.slack_notification_lambda]
  topic_arn = var.ScanResultTopicARN
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_notification_lambda.arn
}
