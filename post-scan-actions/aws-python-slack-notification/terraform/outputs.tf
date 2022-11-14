# Outputs
output "slack_notification_lambda_output" {
   value = aws_lambda_function.SlackNotificationLambda.arn
}
