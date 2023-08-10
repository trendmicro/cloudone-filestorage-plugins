resource "aws_cloudformation_stack" "fss-account-scanner-by-tf" {
  name = var.CFNStackName
  capabilities = ["CAPABILITY_IAM"]

  parameters = {
    KMSKeyARNForDLQSSE = var.KMSKeyARNForDLQSSE
    KMSKeyARNForTopicSSE = var.KMSKeyARNForTopicSSE
    KMSKeyARNsForBucketSSE = var.KMSKeyARNsForBucketSSE
    ReportObjectKey = var.ReportObjectKey
    ObjectCreatedEventFilter = var.ObjectCreatedEventFilter
    ScannerEphemeralStorage = var.ScannerEphemeralStorage
    QuarantineBucket = var.QuarantineBucket
    FSSBucketName = var.FSSBucketName
    FSSKeyPrefix = var.FSSKeyPrefix
    TrendMicroManagementAccount = var.TrendMicroManagementAccount
    CloudOneRegion = var.CloudOneRegion
    ExternalID = var.ExternalID
    EnableCrossAccountScanning = var.EnableCrossAccountScanning
  }

  template_url = var.TemplateURL

}