resource "aws_cloudformation_stack" "fss-storage-by-tf" {
  name = "fss-storage-stack-by-tf"
  capabilities = ["CAPABILITY_IAM"]

  parameters = {
    S3BucketToScan = var.S3BucketToScan,
    ExternalID = var.ExternalID
    CloudOneRegion = var.CloudOneRegion
    AdditionalIAMPolicies = var.AdditionalIAMPolicies
    BucketListenerDLQARN = var.BucketListenerDLQARN
    FSSBucketName = var.FSSBucketName
    FSSKeyPrefix = var.FSSKeyPrefix
    IAMPolicyPrefix = var.IAMPolicyPrefix
    IAMRolePrefix = var.IAMRolePrefix
    KMSKeyARNForBucketSSE = var.KMSKeyARNForBucketSSE
    KMSKeyARNForDLQSSE = var.KMSKeyARNForDLQSSE
    KMSKeyARNForQueueSSE = var.KMSKeyARNForQueueSSE
    KMSKeyARNForTopicSSE = var.KMSKeyARNForTopicSSE
    LambdaFunctionPrefix = var.LambdaFunctionPrefix
    NetworkProxy = var.NetworkProxy
    ObjectFilterPrefix = var.ObjectFilterPrefix
    PermissionsBoundary = var.PermissionsBoundary
    PostScanActionTagDLQARN = var.PostScanActionTagDLQARN
    ReportObjectKey = var.ReportObjectKey
    ScannerAWSAccount = var.ScannerAWSAccount
    ScannerLambdaAliasARN = var.ScannerLambdaAliasARN
    ScannerSQSURL = var.ScannerSQSURL
    ScanOnGetObject = var.ScanOnGetObject
    ScanResultTopicDLQARN = var.ScanResultTopicDLQARN
    SecurityGroupIDs = var.SecurityGroupIDs
    SNSTopicPrefix = var.SNSTopicPrefix
    SubnetIDs = var.SubnetIDs
    TrendMicroManagementAccount = var.TrendMicroManagementAccount
    TriggerWithObjectCreatedEvent = var.TriggerWithObjectCreatedEvent

  }

  template_url="https://file-storage-security.s3.amazonaws.com/latest/templates/FSS-Storage-Stack.template"

}
