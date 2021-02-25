# Other Installation Methods

## Prerequisites

1. **Install supporting tools**
    - Install the AWS command line interface (CLI). See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.
    - Install the AWS SAM command line interface (CLI). See [Installing the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) for details.
    - Install GNU Make if you don't want to use the AWS/SAM CLI. See [GNU Make](https://www.gnu.org/software/make/) for download information.
2. **Create S3 buckets**
    - Create a 'Promote bucket' to receive clean files. Example: `fss-promote`.
    - Create a 'Quarantine bucket' to receive quarantined files. Example: `fss-quarantine`.
    - Create a deployment artifact bucket if you are deploying with SAM CLI. Example: `fss-plugin-poq-deployment`.
3. **Create a custom policy**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **Services > IAM**.
    2. On the left, click **Policies**.
    3. In the main pane, click **Create policy**.
    4. Click the **JSON** tab.
    5. Paste the [JSON code below](#JSON) into the text box, making sure to replace the variables in the JSON code with your own values. Variables are described following the code.
    6. Click **Review policy**.
    7. On the **Review policy** page:
        - In the **Name** field, enter a name. Example: `FSS_Lambda_Policy`.
        - Click **Create policy**.
    8. Take note of the **Policy Name**.
    </details>

    <details>
    <summary>Using the AWS CLI</summary>

    1. Paste the [JSON code below](#JSON) into a file called `fss-trust-policy.json` (or another name) making sure to replace the variables in the JSON code with your own values. Variables are described following the code.
    2. In a shell program such as bash or Windows Powershell, enter the following AWS CLI command to create the policy:

        `aws iam create-policy --policy-name <YOUR_FSS_LAMBDA_POLICY> --policy-document file://fss-trust-policy.json`

        where `<YOUR_FSS_LAMBDA_POLICY>` is replaced with the name you want to give to the custom policy. Example: `FSS_Lambda_Policy`.
    3. In the output, take note of the custom policy's ARN. Example: `arn:aws:iam::0123456789012:policy/FSS_Lambda_Policy`
    </details>

    <details>
    <summary>Using the SAM CLI</summary>
    You can skip this step with SAM CLI.
    </details>

    <details>
    <summary><a name="JSON">JSON code (for use in the custom policy)</a></summary>

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
        {
                "Sid": "CopyFromScanningBucket",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:GetObjectTagging"
                ],
                "Resource": "arn:aws:s3:::<YOUR_BUCKET_TO_SCAN>/*"
            },
            {
                "Sid": "CopyToPromoteOrQuarantineBucket",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectTagging",
                    "s3:PutObjectAcl"
                ],
                "Resource": [
                    "arn:aws:s3:::<YOUR_QUARANTINE_BUCKET>/*",
                    "arn:aws:s3:::<YOUR_PROMOTE_BUCKET>/*"
                ]
            }
        ]
    }
    ```

    - where:
        - `<YOUR_BUCKET_TO_SCAN>` is replaced with your scanning bucket name. You can find this name in AWS > **CloudFormation** > your all-in-one stack > **Resources** > your storage stack > **Outputs > ScanningBucket**.
        - `<YOUR_QUARANTINE_BUCKET>` is replaced with your Quarantine bucket name.
        - `<YOUR_PROMOTE_BUCKET>` is replaced with your Promote bucket name.
    </details>

4. **Create an execution role for the Lambda function**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **Services > IAM**.
    2. Click **Roles** on the left.
    3. In the main pane, click **Create role**.
    4. Under **Select type of trusted entity**:
        - Select the **AWS service** box.
        - Click the  **Lambda** service from the list.
        - Click **Next: Permissions**.
    5. In the search box:
        - Search for `AWSLambdaBasicExecutionRole`.
        - Select its check box.
        - Search for `<YOUR_FSS_LAMBDA_POLICY>` which you created earlier. Example: `FSS_Lambda_Policy`
        - Select its check box in the list.
        - You now have two policies selected.
        - Click **Next: Tags**.
        - (Optional) Enter tags.
        - Click **Next: Review**.
    6. On the **Review** page:
        - In the **Role name** field, enter a name. Example: `FSS_Lambda_Role`.
        - Make sure that two policies are listed.
        - Click **Create role**.
    </details>

   <details>
   <summary>Using the AWS CLI</summary>

    1. Paste the [JSON code below](#JSON_trust-doc) into a file called `trust.json` (or another name).
    2. Enter the following AWS CLI command to create the role:

        `aws iam create-role --role-name <YOUR_FSS_LAMBDA_ROLE> --assume-role-policy-document file://trust.json`

        where `<YOUR_FSS_LAMBDA_ROLE>` is replaced with the name you want to give to the role. Example: `FSS_Lambda_Role`.
    3. Attach the `AWSLambdaBasicExecutionRole` managed policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`

    4. Attach the custom policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Role --policy-arn <YOUR_FSS_LAMBDA_POLICY_ARN>`

        where `<YOUR_FSS_POLICY_ARN>` is replaced with the File Storage Security custom policy's ARN that you noted earlier. Example: `arn:aws:iam::0123456789012:policy/FSS_Lambda_Policy`.
    </details>

    <details>
    <summary>Using the SAM CLI</summary>
    You can skip this step with SAM CLI.
    </details>

    <details>
    <summary><a name="JSON_trust-doc">JSON code (for use in the trust document)</a></summary>

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    ```

    </details>

## Deploy the Lambda

<details>
<summary>Using the AWS console</summary>

1. **Create an empty function**
    - Go to **Services > Lambda**.
    - Click **Create function**.
    - Select the **Author from scratch** box.
    - In the **Function name** field, enter a name. Example: `FSS_Prom_Quar_Lambda`.
    - From the **Runtime** drop-down list, select **Python 3.8**.
    - Under **Permissions**, expand **Choose or create an execution role**.
    - Select **Use an existing role**.
    - In the drop-down list, select the execution role you created earlier. Example: `FSS_Lambda_Role`.
    - Click **Create function** and leave the page open.
2. **Add function code**
    - Download the 'Promote or Quarantine' [handler.py file from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-promote-or-quarantine/handler.py).
    - On the AWS console page you left open, in the **Function code** section, remove the sample Lambda function code and paste the code from `handler.py`.
    - Click **Deploy** and leave the page open.
3. **Add environment variables**
    - Scroll to the **Environment variables** section.
    - Click **Edit** (on the right).
    - Click **Add environment variable**
        - In the **Key** field, enter `PROMOTEBUCKET`
        - In the **Value** field, enter `<YOUR_PROMOTE_BUCKET>`
    - Again, click **Add environment variable**
        - In the **Key** field, enter `QUARANTINEBUCKET`
        - In the **Value** field, enter `<YOUR_QUARANTINE_BUCKET>` . Example: `fss-quarantine`
    - Click **Save** to save both variables.
4. **Adjust timeout**
    - Scroll to the **Basic settings** section.
    - Click **Edit** (on the right).
    - Set the **Timeout** to 30.
    - Click **Save** to save settings.

</details>

<details>
<summary>Using the AWS CLI</summary>

1. Download the 'Promote or Quarantine' [handler.py file from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-promote-or-quarantine/handler.py).
2. In a shell program, create a deployment package:

    `zip zip/<YOUR_ZIP_NAME>.zip handler.py`

    where `<YOUR_ZIP_NAME>` is replaced with the name you want to give your Lambda function. Example: `promote-or-quarantine`.
3. Create the Lambda function, using backslashes (`\`) to separate the lines, as shown below:

    ```bash
    aws lambda create-function --function-name <YOUR_FSS_FUNC_NAME> \
    --role <YOUR_FSS_LAMBDA_ROLE> \
    --runtime python3.8 \
    --timeout 30 \
    --memory-size 512 \
    --handler handler.lambda_handler \
    --zip-file fileb://zip/<YOUR_ZIP_NAME>.zip \
    --environment Variables=\{PROMOTEBUCKET=<YOUR_PROMOTE_BUCKET>,QUARANTINEBUCKET=<YOUR_QUARANTINE_BUCKET>\}
    ```

- where:
    - `<YOUR_FSS_FUNC_NAME>` is replaced with the name you want to give your Lambda function. Example: `FSS_Prom_Quar_Lambda`.
    - `<YOUR_FSS_LAMBDA_ROLE>` is replaced with the ARN of the role you previously created for the Lambda function. You can find the ARN in the AWS console under **Services > IAM > Roles** > your role > **Role ARN** field (at the top). Example: `arn:aws:iam::012345678901:role/FSS_Lambda_Role`.
    - `<YOUR_ZIP_NAME>` is replaced with the name of the ZIP file you created earlier. Example: `promote-or-quarantine`
    - `<YOUR_PROMOTE_BUCKET>` is replaced with the name of your 'Promote bucket' as it appears in S3.
    - `<YOUR_QUARANTINE_BUCKET>` is replaced with the name of your 'Quarantine bucket' as it appears in S3.

</details>

<details>
<summary>Using the SAM CLI</summary>

1. Clone this repository.
2. [Find the 'ScanResultTopic' SNS topic ARN](#subscribe-the-lambda-to-the-sns-topic)
3. Run `sam deploy` with the your parameters.

    ```bash
    cd post-scan-actions/aws-python-promote-or-quarantine
    sam deploy \
        --s3-bucket <YOUR_DEPLOYMENT_ARTIFACT_BUCKET> \
        --stack-name <YOUR_STACK_NAME> \
        --parameter-overrides \
            PromoteBucketName=<YOUR_PROMOTE_BUCKET> \
            PromoteMode=move \
            QuarantineBucketName=<YOUR_QUARANTINE_BUCKET> \
            QuarantineMode=move \
            ACL=bucket-owner-full-control \
            ScanResultTopicARN=<YOUR_SCAN_RESULT_TOPIC> \
            ScanningBucketName=<YOUR_SCANNING_BUCKET> \
        --capabilities CAPABILITY_IAM
    ```

</details>

<details>
<summary>Using the Makefile</summary>

1. Download the 'Promote or Quarantine' [Makefile from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-promote-or-quarantine/Makefile).
2. In a shell program, enter the following GNU Make command, using backslashes (`\`) to separate lines, as shown below:

    ```bash
    FUNCTION_NAME=<YOUR_FSS_FUNC_NAME> ROLE_ARN=<YOUR_FSS_ROLE_ARN> \
    PROMOTE_BUCKET=<YOUR_PROMOTE_BUCKET> QUARANTINE_BUCKET=<YOUR_QUARANTINE_BUCKET> \
    make create-function
    ```

- where:
    - `<YOUR_FSS_FUNC_NAME>` is replaced with the name you want to give your Lambda function. Example: `FSS_Prom_Quar_Lambda`.
    - `<YOUR_FSS_ROLE_ARN>` is replaced with the ARN of the role you previously created for the Lambda function. You can find the ARN in the AWS console under **Services > IAM > Roles** > your role > **Role ARN** field (at the top). Example: `arn:aws:iam::012345678901:role/FSS_Lambda_Role`.
    - `<YOUR_PROMOTE_BUCKET>` is replaced with the name of your 'Promote bucket' as it appears in S3.
    - `<YOUR_QUARANTINE_BUCKET>` is replaced with the name of your 'Quarantine bucket' as it appears in S3.

</details>

## Subscribe the Lambda to the SNS topic

1. **Find the 'ScanResultTopic' SNS topic ARN**
    - In the AWS console, go to **Services > CloudFormation** > your all-in-one stack > **Resources** > your storage stack > **Resources**.
    - Scroll down to locate the  **ScanResultTopic** Logical ID.
    - Copy the **ScanResultTopic** ARN to a temporary location. Example: `arn:aws:sns:us-east-1:123445678901:FileStorageSecurity-All-In-One-Stack-StorageStack-1IDPU1PZ2W5RN-ScanResultTopic-N8DD2JH1GRKF`
2. **Find the Lambda function ARN**

    📌 The Lambda function ARN is only required if you plan to use the AWS CLI (as opposed to the console) to subscribe the Lambda to the SNS topic.
    - In the AWS console, go to **Services > Lambda**.
    - Search for the Lambda function you created previously. Example: `FSS_Prom_Quar_Lambda`
    - Click the Lambda function link.
    - On the top-left, locate the **ARN**.
    - Copy the ARN to a temporary location. Example: `arn:aws:lambda:us-east-1:123445678901:function:FSS_Prom_Quar_Lambda`
3. **Subscribe the Lambda to the SNS topic**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **Services > Lambda**.
    2. Search for the Lambda function you created previously. Example: `FSS_Prom_Quar_Lambda`
    3. Click the link to your Lambda function to view its details.
    4. Click **Add trigger** on the left.
    5. From the **Trigger configuration** list, select **SNS**.
    6. In the **SNS topic** field, enter the SNS topic ARN you found earlier.
    7. Click **Add**. Your Lambda is now subscribed to the SNS topic.

    </details>

    <details>
    <summary>Using the AWS CLI</summary>

    - Grant the Lambda function permissions to attach a trigger via AWS CLI command:

        ```bash
        aws lambda add-permission --function-name <YOUR_FSS_FUNC_NAME> \
        --source-arn <SNS_TOPIC_ARN> \
        --statement-id <YOUR_FSS_FUNC_NAME> --action "lambda:InvokeFunction" \
        --principal sns.amazonaws.com
        ```

    - Enter the following AWS CLI command to subscribe your Lambda function to the SNS topic:

        `aws sns subscribe --topic-arn <SNS_Topic_ARN> --notification-endpoint <YOUR_LAMBDA_FUNCTION_ARN> --protocol lambda`
    - where:
        - `<SNS_TOPIC_ARN>` is replaced with the SNS topic ARN you found earlier.
        - `<YOUR_LAMBDA_FUNCTION_ARN>` is replaced with the Lambda function ARN you found earlier.
    </details>

    <details>
    <summary>Using the SAM CLI</summary>
    You can skip this step with SAM CLI.
    </details>

## Test the Lambda

To test that the Lambda function was deployed properly, you'll need to generate a malware detection using the [eicar test file](https://secure.eicar.org/eicar.com "A file used for testing anti-malware scanners."), and then check the Quarantine bucket to make sure the `eicar` file was sent there successfully.

1. **Download the Eicar test file**
   - Temporarily disable your virus scanner or create an exception, otherwise it will catch the `eicar` file and delete it.
   - Browser: Go to the [eicar file](https://secure.eicar.org/eicar.com) page and download `eicar_com.zip` or any of the other versions of this file.
   - CLI: `curl -O https://secure.eicar.org/eicar_com.zip`
2. **Upload the eicar file to the ScanningBucket**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **CloudFormation > Stacks** > your all-in-one stack > your nested storage stack.
    2. In the main pane, click the **Outputs** tab and then copy the **ScanningBucket** string. Search the string in Amazon S3 console to find your ScanningBucket.
    3. Click **Upload** and upload `eicar_com.zip`. File Storage Security scans the file and detects malware.
    4. Still in S3, go to your Quarantine bucket and make sure that `eicar.zip` file is present.
    5. Go back to your ScanningBucket and make sure the `eicar.zip` is no longer there.

    📌 It can take 15-30 seconds or more for the 'move' operation to complete, and during this time, you may see the file in both buckets.
    </details>

    <details>
    <summary>Using the AWS CLI</summary>

    - Enter the folowing AWS CLI command to upload the Eicar test file to the scanning bucket:

        `aws s3 cp eicar_com.zip s3://<YOUR_SCANNING_BUCKET>`
    - where:
        - `<YOUR_SCANNING_BUCKET>` is replaced with the ScanningBucket name.

    **NOTE:** It can take about 15-30 seconds or more for the file to move.
    </details>

## Optional Configuration

Additional options are supported as described in the following section.

- **Skip promotion/quarantine**
    - If you wish to _only_ promote or _only_ quarantine, remove the environment variable corresponding to the action you want to ignore. For example, to skip quarantine and promote only, remove the `QUARANTINEBUCKET` environment variable from the scanner Lambda configuration.
- **Custom ACL (Access Control List)**
    - An access control list (ACL) [defines which AWS accounts or groups are granted access and the type of access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl_overview.html).
    - You can set a specific object ACL for promoted/quarantined objects. For example, if your source bucket has restricted permissions and you wish to grant wider access to promoted/quarantined objects, set the `ACL` environment variable in the scanner Lambda configuration, i.e., the value `bucket-owner-full-control` grants the promote/quarantine bucket access to the object as if it were there own.
- **Change default promotion/quarantine behavior**
    - By default when an object is promoted or quarantined, it is _moved_ from the source bucket into either one of `PROMOTEBUCKET` or `QUARANTINEBUCKET`. That is, it's removed from the scanned bucket and placed in the destination bucket. If, for example, you wish to instead perform a _copy_ on promotion (i.e., pseudo object replication-like behavior) then set the `PROMOTEMODE` environment variable in the scanner Lambda configuration to `copy` (default: `move`). Likewise, you _could_ do the same for quarantine by setting the `QUARANTINEMODE` variable to `copy` (though strongly **not** recommended).
