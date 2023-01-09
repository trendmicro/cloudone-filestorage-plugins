# Required Variables

variable "AWSRegion" {
  type = string
  default = ""
  description = "The AWS Region that the Stack will run"
}

variable "S3BucketToScan" {
  type = string
  default = ""
  description = "The S3 bucket to scan. Specify an existing S3 bucket."
}

variable "ExternalID" {
  type = string
  default = ""
  description = "The External ID is for future use with updating Lambdas and also to address and prevent the 'confused deputy' problem."
}

variable "CloudOneRegion" {
  type = string
  default = "us-1"
  description = "The region of the Trend Micro Cloud One services."
}

# Optional Variables - Warning: Do not modify this field when you update the stack. Modifications may cause your update to fail.

variable "AdditionalIAMPolicies" {
  type = string
  default = ""
  description = "A comma-separated list of IAM policy ARNs to attach to all the roles that will be created."
}

variable "BucketListenerDLQARN" {
  type = string
  default = ""
  description = "The SQS ARN for BucketListenerLambda DLQ."
}

variable "FSSBucketName" {
  type = string
  default = "file-storage-security"
  description = "File Storage Security bucket name can include numbers, lowercase letters, uppercase letters, and hyphens (-). It cannot start or end with a hyphen (-)."
}

variable "FSSKeyPrefix" {
  type = string
  default = "latest/"
  description = "File Storage Security key prefix can include numbers, lowercase letters, uppercase letters, hyphens (-), and forward slash (/)."
}

variable "IAMPolicyPrefix" {
  type = string
  default = ""
  description = "Prefix for the name of the IAM Policies. Must end with a hyphen (-)."
}

variable "IAMRolePrefix" {
  type = string
  default = ""
  description = "Prefix for the name of the IAM roles being deployed. Must end with a hyphen (-)."
}

variable "KMSKeyARNForBucketSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master key used to encrypt S3 bucket objects. Leave it blank if you haven't enabled SSE-KMS for the bucket."
}

variable "KMSKeyARNForDLQSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master key used to encrypt messages of DLQ for storage stack. Leave it blank if you haven't used your own CMK for SQS server-side encryption on the queue ARNs you provided."
}

variable "KMSKeyARNForQueueSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master key used to encrypt messages in SQS. Leave it blank if you haven't used your own CMK for SQS server-side encryption."
}

variable "KMSKeyARNForTopicSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master key used to encrypt messages in SNS. Leave it blank if you haven't used your own CMK for SNS server-side encryption."
}

variable "LambdaFunctionPrefix" {
  type = string
  default = ""
  description = "Prefix for the name of the Lambda functions being deployed. Must end with a hyphen (-)."
}

variable "LambdaLayerPrefix" {
  type = string
  default = ""
  description = "Prefix for the name of the Lambda layers being deployed. Must end with a hyphen (-)."
}

variable "NetworkProxy" {
  type = string
  default = ""
  description = "Network proxy setting in the format scheme://[user:pass@]host:port, for example http://proxy.server:8080. Leave it blank if you don't want Lambda functions to connect to an explicit proxy in the VPC."
}

variable "ObjectFilterPrefix" {
  type = string
  default = ""
  description = "Limit the scan to objects whose key starts with the specified characters."
}

variable "PermissionsBoundary" {
  type = string
  default = ""
  description = "he ARN of the policy used to set the permissions boundary for all the roles that will be created."
}

variable "PostScanActionTagDLQARN" {
  type = string
  default = ""
  description = "The SQS ARN for PostScanActionTag DLQ."
}

variable "ReportObjectKey" {
  type = bool
  default = false
  description = "Enable this to report the object keys of the scanned objects to File Storage Security backend services. File Storage Security can then display the object keys of the malicious objects in the response of events API."
}

variable "ScannerEphemeralStorage" {
  type = number
  default = 512
  description = "The size of the scanner lambda function's temp directory in MB. The default value is 512, but it can be any whole number between 512 and 2048 MB. Configure a large ephemeral storage to scan larger files in zip files. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html#configuration-ephemeral-storage"
}

variable "ScanOnGetObject" {
  type = bool
  default = false
  description = "Scan objects retrieved (GET requests) from S3 with the Object Lambda Access Point. This option requires that the storage stack is deployed in both the same account and the same region as the scanner stack. For more information, see https://cloudone.trendmicro.com/docs/file-storage-security/aws-scan-on-get-object/"
}

variable "ScanResultTopicDLQARN" {
  type = string
  default = ""
  description = "The SQS ARN for ScanResultTopic DLQ."
}

variable "SecurityGroupIDs" {
  type = string
  default = ""
  description = "A comma-separated list of VPC Security Group IDs that are attached to Lambda functions. Leave it blank if you don't want to attach Lambda functions to a VPC."
}

variable "SNSTopicPrefix" {
  type = string
  default = ""
  description = "Prefix for SNS topic name can be empty or include include alphanumeric characters, hyphens (-) and underscores (_) and must end with a hyphen. The maximum length is 50 characters."
}

variable "SQSQueuePrefix" {
  type = string
  default = ""
  description = "Prefix for SQS queue name can be empty or include alphanumeric characters, hyphens (-), and underscores (_) and must end with a hyphen. The maximum length is 50 characters."
}

variable "SubnetIDs" {
  type = string
  default = ""
  description = "A comma-separated list of VPC Subnet IDs that are attached to Lambda functions. Leave it blank if you don't want to attach Lambda functions to a VPC."
}

variable "TrendMicroManagementAccount" {
  type = number
  default = 415485722356
  description = "This account will be given permission to modify the stacks for upgrades and troubleshooting purposes."
}

variable "TriggerWithObjectCreatedEvent" {
  type = bool
  default = true
  description = "f the s3:ObjectCreated:* event of the S3BucketToScan is in use, set this option to false. Then trigger the scans by invoking the deployed BucketListenerLambda."
}
