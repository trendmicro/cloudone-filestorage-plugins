resource "aws_cloudformation_stack" "fss-allinone-by-tf" {
  name = "fss-allinone-stack-by-tf"
  capabilities = ["CAPABILITY_IAM"]

  parameters = {
    S3BucketToScan = var.S3BucketToScan,
    ExternalID = var.ExternalID
    CloudOneRegion = var.CloudOneRegion
    AdditionalIAMPolicies = var.AdditionalIAMPolicies
    BucketListenerDLQARN = var.BucketListenerDLQARN
    FSSKeyPrefix = var.FSSKeyPrefix
    IAMPolicyPrefix = var.IAMPolicyPrefix
    IAMRolePrefix = var.IAMRolePrefix
    KMSKeyARNForBucketSSE = var.KMSKeyARNForBucketSSE
    KMSKeyARNForDLQSSE = var.KMSKeyARNForDLQSSE
    KMSKeyARNForQueueSSE = var.KMSKeyARNForQueueSSE
    KMSKeyARNForTopicSSE = var.KMSKeyARNForTopicSSE
    LambdaFunctionPrefix = var.LambdaFunctionPrefix
    LambdaLayerPrefix = var.LambdaLayerPrefix
    NetworkProxy = var.NetworkProxy
    ObjectFilterPrefix = var.ObjectFilterPrefix
    PermissionsBoundary = var.PermissionsBoundary
    PostScanActionTagDLQARN = var.PostScanActionTagDLQARN
    ReportObjectKey = var.ReportObjectKey
    ScannerEphemeralStorage = var.ScannerEphemeralStorage
    ScanOnGetObject = var.ScanOnGetObject
    ScanResultTopicDLQARN = var.ScanResultTopicDLQARN
    SecurityGroupIDs = var.SecurityGroupIDs
    SNSTopicPrefix = var.SNSTopicPrefix
    SQSQueuePrefix = var.SQSQueuePrefix
    SubnetIDs = var.SubnetIDs
    TrendMicroManagementAccount = var.TrendMicroManagementAccount
    TriggerWithObjectCreatedEvent = var.TriggerWithObjectCreatedEvent
  }

  template_url="https://file-storage-security.s3.amazonaws.com/latest/templates/FSS-All-In-One.template"

}
