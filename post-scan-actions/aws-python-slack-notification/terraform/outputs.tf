# Outputs
output "SlackNotificationLambda" {
   value = aws_lambda_function.SlackNotificationLambda.arn
}