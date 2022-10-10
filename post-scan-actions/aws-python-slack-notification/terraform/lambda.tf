# Zip the lambda code
data "archive_file" "zip_the_python_code" {
type        = "zip"
source_file = "../handler.py"
output_path = "${path.module}/lambda_zip/handler.zip"
}

# Create the lambda function
resource "aws_lambda_function" "SlackNotificationLambda" {
  filename      = "${path.module}/lambda_zip/handler.zip"
  function_name = "SlackNotificationLambda"
  role          = aws_iam_role.SlackNotificationLambdaRole.arn
  handler       = "handler.lambda_handler"
  memory_size = 512
  timeout = 30
  runtime = "python3.8"
  tracing_config {
      mode = "Active"
    }
  environment {
    variables = {
      SLACK_URL= var.SlackWebhookURL
      SLACK_CHANNEL= var.SlackChannel
      SLACK_USERNAME= var.SlackUsername
    }
  }
}

# Allows Lambda to add a trigger to SNS
resource "aws_lambda_permission" "SlackNotificationLambdaPermission" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.SlackNotificationLambda.arn}"
    principal = "sns.amazonaws.com"
    source_arn = "${var.ScanResultTopicARN}"
}

# Create the sns event source mapping to lambda
resource "aws_sns_topic_subscription" "ScanResult" {
  depends_on = [aws_lambda_function.SlackNotificationLambda]
  topic_arn = var.ScanResultTopicARN
  protocol  = "lambda"
  endpoint  = aws_lambda_function.SlackNotificationLambda.arn
}