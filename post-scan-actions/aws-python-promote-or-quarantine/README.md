# Post Scan Action - Promote or Quarantine

After a scan occurs, this example Lambda function places clean files in one bucket (a 'Promote' bucket) and malicious files in another (a 'Quarantine' bucket).

## Prerequisites

1. **Install supporting tools**
    - Install the AWS command line interface (CLI). See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.
    - Install GNU Make if you don't want to use the AWS CLI. See [GNU Make](https://www.gnu.org/software/make/) for download information.
2. **Create two S3 buckets**
    - Create a 'Promote bucket' to receive clean files.
    - Create a 'Quarantine bucket' to receive quarantined files.
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
    8. Click the link to your policy to open its summary.
    9. Take note of the **Policy ARN** near the top of the page.
    </details>
    
    <details>
    <summary>Using the AWS CLI</summary>

    1. Paste the [JSON code below](#JSON) into a file called `fss-trust-policy.json` (or another name) making sure to replace the variables in the JSON code with your own values. Variables are described following the code. 
    2. In a shell program such as bash or Windows Powershell, enter the following AWS CLI command to create the policy:

        `aws create-policy --policy-name <YOUR_FSS_LAMBDA_POLICY> --policy-document file://fss-trust-policy.json`

        where `<YOUR_FSS_LAMBDA_POLICY>` is replaced with the name you want to give to the custom policy. Example: `FSS_Lambda_Policy`.
    3. In the output, take note of the custom policy's ARN. Example: `arn:aws:iam::0123456789012:policy/FSS_Lambda_Policy`
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
                        "s3:PutObjectTagging"
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
        - `<YOUR_BUCKET_TO_SCAN>` is replaced with your scanning bucket name. You can find this name in AWS > **CloudFormation** > your all-in-one stack > **Resources** > your storage stack > **Resources > ScanningBucket**. 
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
        - Search for ` AWSLambdaBasicExecutionRole`.
        - Select its check box.
        - Search for `<YOUR_FSS_LAMBDA_POLICY>` where `<YOUR_FSS_LAMBDA_POLICY>` is the name of your custom File Storage Security policy. Example: `FSS_Lambda_Policy`.
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

    1. Enter the following AWS CLI command to create the role:

        `aws iam create-role --role-name <YOUR_FSS_LAMBDA_ROLE>`

        where `<YOUR_FSS_LAMBDA_ROLE>` is replaced with the name you want to give to the role. Example: `FSS_Lambda_Role`.
    2. Attach the `AWSLambdaBasicExecutionRole` managed policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`

    3. Attach the custom policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Role --policy-arn <YOUR_FSS_LAMBDA_POLICY_ARN>`

        where `<YOUR_FSS_POLICY_ARN>` is replaced with the File Storage Security custom policy's ARN that you noted earlier. Example: `arn:aws:iam::0123456789012:policy/FSS_Lambda_Policy`.
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
    - Click **Save** at leave the page open.
3. **Add environment variables**
    - Scroll to the **Environment variables** section.
    - Click **Edit** (on the right).
    - Click **Add environment variable**
        - In the **Key** field, enter `PROMOTEBUCKET` 
        - In the **Value** field, enter `fss-test-promote`
    - Again, click **Add environment variable**
        - In the **Key** field, enter `QUARANTINEBUCKET` 
        - In the **Value** field, enter `fss-test-quarantine`
    - Click **Save** to save both variables.
4. **Adjust timeout**
    -  Scroll to the **Basic settings** section.
    -  Click **Edit** (on the right).
    -  Set the **Timeout** to 30.
    -  Click **Save** to save settings.

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
    
    📌 The Lamdba function ARN is only required if you plan to use the AWS CLI (as opposed to the console) to subscribe the Lambda to the SNS topic.
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

    - Enter the following AWS CLI command to subscribe your Lamdba function to the SNS topic:
        
        `aws sns subscribe --topic-arn <SNS_Topic_ARN> --notification-endpoint <YOUR_LAMBDA_FUNCTION_ARN>`
    - where:
        - `<SNS_TOPIC_ARN>` is replaced with the SNS topic ARN you found earlier.
        - `<YOUR_LAMBDA_FUNCTION_ARN>` is replaced with the Lambda function ARN you found earlier.
    </details>

