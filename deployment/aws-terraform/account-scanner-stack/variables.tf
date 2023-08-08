variable "AWSRegion" {
  type = string
  default = ""
  description = "The AWS Region that the Stack will run"
}

variable "KMSKeyARNForDLQSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master key used to encrypt messages in SQS. Leave it blank if you haven't used your own CMK for SQS server-side encryption."
}

variable "KMSKeyARNForTopicSSE" {
  type = string
  default = ""
  description = "The ARN for the KMS master keys used to encrypt messages in SNS scanResultTopic. Leave it blank if you haven't used your own CMK for SNS server-side encryption."
}

variable "KMSKeyARNsForBucketSSE" {
  type = string
  default = ""
  description = "A comma-separated list of ARNs for the KMS master keys used to encrypt S3 bucket objects. Leave it blank if you haven't enabled SSE-KMS for the buckets."
}

variable "ReportObjectKey" {
  type = bool
  default = false
  description = "Enable this to report the object keys of the scanned objects to File Storage Security backend services. File Storage Security can then display the object keys of the malicious objects in the response of events API."
}

variable "ObjectCreatedEventFilter" {
  type = string
  default = ""
  description = "The event pattern to filter the object created event. Please provide a JSON string of event pattern detail. For example, {\"bucket\":{\"name\":[{\"prefix\":\"bucket_prefix_to_scan\"}]},\"object\":{\"key\":[{\"prefix\":\"object_key_prefix_to_scan\"}]}}."
}

variable "ScannerEphemeralStorage" {
  type = number
  default = 512
  description = "The size of the scanner lambda function's temp directory in MB. The default value is 512, but it can be any whole number between 512 and 2048 MB. Configure a large ephemeral storage to scan larger files in zip files. For more information, see https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html#configuration-ephemeral-storage"
}

variable "QuarantineBucket" {
  type = string
  default = ""
  description = "[Optional] The bucket to quarantine malicious files. The bucket region should be the same region as the account scanner stack. Leave the bucket blank to disable quarantining"
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

variable "TrendMicroManagementAccount" {
  type = number
  default = 415485722356
  description = "This account will be given permission to modify the stacks for upgrades and troubleshooting purposes."
}

variable "CloudOneRegion" {
  type = string
  default = "us-1"
  description = "The region of the Trend Micro Cloud One services."
}

variable "ExternalID" {
  type = string
  default = ""
  description = "The External ID is for future use with updating Lambdas and also to address and prevent the 'confused deputy' problem."
}

variable "EnableCrossAccountScanning" {
  type = bool
  default = false
  description = "Enable cross account scanning within the same organization."
}
