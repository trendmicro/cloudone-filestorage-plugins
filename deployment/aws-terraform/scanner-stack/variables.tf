# Required Variables

variable "AWSRegion" {
  type = string
  default = ""
  description = "The AWS Region that the Stack will run"
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

variable "FSSBucketName" {
  type = string
  default = "file-storage-security"
  description = "File Storage Security bucket name can include numbers, lowercase letters, and hyphens (-). It cannot start or end with a hyphen (-)."
}

variable "FSSKeyPrefix" {
  type = string
  default = "latest/"
  description = "The File Storage Security key prefix can include numbers, lowercase letters, uppercase letters, hyphens (-), and forward slash (/)."
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

variable "KMSKeyARNForQueueSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master key used to encrypt messages in SQS. Leave it blank if you haven't used your own CMK for SQS server-side encryption."
}

variable "KMSKeyARNsForTopicSSE" {
  type = string
  default = ""
  description = "A comma-separated list of ARNs for the KMS master keys used to encrypt messages in SNS scanResultTopic. Leave it blank if you haven't used your own CMK for SNS server-side encryption."
}


variable "LambdaFunctionPrefix" {
  type = string
  default = ""
  description = "Prefix for Lambda function name can be empty or include letters, numbers, hyphens (-), and underscores (_) and must end with a hyphen. The maximum length is 50 characters."
}

variable "KMSKeyARNsForTopicSSE" {
  type = string
  default = ""
  description = "A comma-separated list of ARNs for the KMS master keys used to encrypt messages in SNS scanResultTopic. Leave it blank if you haven't used your own CMK for SNS server-side encryption."
}


variable "LambdaFunctionPrefix" {
  type = string
  default = ""
  description = "Prefix for Lambda function name can be empty or include letters, numbers, hyphens (-), and underscores (_) and must end with a hyphen. The maximum length is 50 characters."
}

variable "LambdaLayerPrefix" {
  type = string
  default = ""
  description = "Prefix for the name of the Lambda layers being deployed. Must end with a hyphen (-)."
}

variable "NetworkProxy" {
  type = string
  default = ""
  description = "Network proxy setting in the format scheme://[user:pass@]host:port. For example http://proxy.server:8080. Leave it blank if you don't want Lambda functions to connect to an explicit proxy in the VPC."
}

variable "PermissionsBoundary" {
  type = string
  default = ""
  description = "The ARN of the policy used to set the permissions boundary for all the roles that will be created."
}

variable "ScannerEphemeralStorage" {
  type = number
  default = 512
  description = "The size of the scanner lambda function's temp directory in MB. The default value is 512, but it can be any whole number between 512 and 2048 MB. Configure a large ephemeral storage to scan larger files in zip files. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common html#configuration-ephemeral-storage"
}

variable "SecurityGroupIDs" {
  type = string
  default = ""
  description = "A comma-separated list of the VPC Security Group IDs that are attached to Lambda functions. Leave it blank if you don't want to attach Lambda functions to a VPC."
}

variable "SQSQueuePrefix" {
  type = string
  default = ""
  description = "Prefix for the name of SQS queues being deployed. Must end with a hyphen (-)."
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
