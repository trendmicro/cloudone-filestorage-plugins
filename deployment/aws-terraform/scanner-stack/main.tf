resource "aws_cloudformation_stack" "fss-scanner-by-tf" {
  name = "fss-scanner-stack-by-tf"
  capabilities = ["CAPABILITY_IAM"]

  parameters = {
    ExternalID = var.ExternalID
    CloudOneRegion = var.CloudOneRegion
    AdditionalIAMPolicies = var.AdditionalIAMPolicies
    FSSBucketName = var.FSSBucketName
    FSSKeyPrefix = var.FSSKeyPrefix
    IAMPolicyPrefix = var.IAMPolicyPrefix
    IAMRolePrefix = var.IAMRolePrefix
    KMSKeyARNForQueueSSE = var.KMSKeyARNForQueueSSE
    KMSKeyARNsForTopicSSE = var.KMSKeyARNsForTopicSSE
    LambdaFunctionPrefix = var.LambdaFunctionPrefix
    LambdaLayerPrefix = var.LambdaLayerPrefix
    NetworkProxy = var.NetworkProxy
    ScannerEphemeralStorage = var.ScannerEphemeralStorage
    SecurityGroupIDs = var.SecurityGroupIDs
    SQSQueuePrefix = var.SQSQueuePrefix
    SubnetIDs = var.SubnetIDs
    TrendMicroManagementAccount = var.TrendMicroManagementAccount
  }

  template_url="https://file-storage-security.s3.amazonaws.com/latest/templates/FSS-Scanner-Stack.template"

}
