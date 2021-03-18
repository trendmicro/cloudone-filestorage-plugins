# Cloud One File Storage Security Post Scan Action - Conformity Custom Check

After a scan occurs and a malicious file is detected, this example Lambda function creates a custom check within Cloud One Conformity.

## Prerequisites

1. **Configure Conformity API Key**
    - Log into Conformity and select your username and select `User settings`.
    - Select `API Keys`.
    - Select `+ New API Key`, then select `Generate Key`.
    - Copy the generated API Key for use later when installing the function.
2. **Find the 'ScanResultTopicARN' SNS topic ARN**
    - In the AWS console, go to **Services > CloudFormation** > your all-in-one stack > **Outputs**  or **Services > CloudFormation** > your storage stack > **Outputs**.
    - Scroll down to locate the  **ScanResultTopicARN** Key.
    - Copy the **ScanResultTopic** ARN to a temporary location. Example: `arn:aws:sns:us-east-1:123445678901:FileStorageSecurity-All-In-One-Stack-StorageStack-1IDPU1PZ2W5RN-ScanResultTopic-N8DD2JH1GRKF`

## Installation

### From AWS Lambda Console

1. Visit [the app's page on the AWS Lambda Console](https://console.aws.amazon.com/lambda/home?#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:415485722356:applications/cloudone-filestorage-plugin-action-conformity-custom-check).
2. Fill in the parameters.
3. Select the `I acknowledge that this app creates custom IAM roles.` checkbox.
4. Select `Deploy`.

### Embed as a Nested App in Your Serverless Application

1. Visit [the app's page on the AWS Lambda Console](https://console.aws.amazon.com/lambda/home?#/create/app?applicationId=arn:aws:serverlessrepo:us-east-1:415485722356:applications/cloudone-filestorage-plugin-action-conformity-custom-check).
2. Select the `Copy as SAM Resource` button and paste the copied YAML into your SAM template, filling in any required parameters.

## Test the Application

To test that the application was deployed properly, you'll need to generate a malware detection using the [eicar test file](https://secure.eicar.org/eicar.com "A file used for testing anti-malware scanners."), and then check the Quarantine bucket to make sure the `eicar` file was sent there successfully.

1. **Download the Eicar test file**
   - Temporarily disable your virus scanner or create an exception, otherwise it will catch the `eicar` file and delete it.
   - Browser: Go to the [eicar file](https://secure.eicar.org/eicar.com) page and download `eicar_com.zip` or any of the other versions of this file.
   - CLI: `curl -O https://secure.eicar.org/eicar_com.zip`
2. **Upload the eicar file to the ScanningBucket**

    - Using the AWS console

        1. Go to **CloudFormation > Stacks** > your all-in-one stack > your nested storage stack.
        2. In the main pane, select the **Outputs** tab and then copy the **ScanningBucket** string. Search the string in Amazon S3 console to find your ScanningBucket.
        3. Select **Upload** and upload `eicar_com.zip`. File Storage Security scans the file and detects malware.
        4. Within Conformity select **Browse All Checks** you should now see the malicious file finding under the Check ID specified when creating the function. Example: `CUSTOM-001`

        > 📌 It can take 15-30 seconds for the event to appear within Conformity.

    - Using the AWS CLI

        - Enter the folowing AWS CLI command to upload the Eicar test file to the scanning bucket:
            `aws s3 cp eicar_com.zip s3://<YOUR_SCANNING_BUCKET>`
        - where:
            - `<YOUR_SCANNING_BUCKET>` is replaced with the ScanningBucket name.

        > 📌 It can take 15-30 seconds for the event to appear within Conformity.
