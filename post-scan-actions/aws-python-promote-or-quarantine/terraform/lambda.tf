# Zip the lambda code
data "archive_file" "zip_the_python_code" {
  type        = "zip"
  source_file = "../handler.py"
  output_path = "../handler.zip"
}

# Create the lambda function
resource "aws_lambda_function" "PromoteOrQuarantineLambda" {
  filename      = "../handler.zip"
  function_name = "PromoteOrQuarantineLambda"
  role          = aws_iam_role.PromoteOrQuarantineLambdaRole.arn
  handler       = "handler.lambda_handler"
  memory_size = 512
  timeout = 30
  runtime = "python3.8"
  tracing_config {
      mode = "Active"
  }
  environment {
    variables = {
      PROMOTEBUCKET= var.promote_bucket_name
      PROMOTEMODE= var.promote_mode
      QUARANTINEBUCKET= var.quarantine_bucket_name
      QUARANTINEMODE= var.quarantine_mode
      ACL= var.acl
    }
  }
}

# Allows Lambda to add a trigger to SNS
resource "aws_lambda_permission" "PromoteOrQuarantineLambdaPermission" {
    statement_id = "AllowExecutionFromSNS"
    action = "lambda:InvokeFunction"
    function_name = "${aws_lambda_function.PromoteOrQuarantineLambda.arn}"
    principal = "sns.amazonaws.com"
    source_arn = "${var.scan_result_topic_arn}"
}

# Create the sns event source mapping to lambda
resource "aws_sns_topic_subscription" "ScanResult" {
  depends_on = [aws_lambda_function.PromoteOrQuarantineLambda]
  topic_arn = var.scan_result_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.PromoteOrQuarantineLambda.arn
}
