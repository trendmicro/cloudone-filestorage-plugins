# Outputs
output "ScanResult" {
   value = aws_lambda_function.PromoteOrQuarantineLambda.arn
}

output "PromoteOrQuarantineLambda" {
   value = aws_lambda_function.PromoteOrQuarantineLambda.arn
}
