# Post Scan Action - Email Notification

After a scan occurs, this example Lambda function sends out a notification Email using Amazon Simple Email Service when a malicious file got detected.

## Prerequisites

1. **Install supporting tools**
    - Install the AWS command line interface (CLI). See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.
    - Install GNU Make if you don't want to use the AWS CLI. See [GNU Make](https://www.gnu.org/software/make/) for download information.
2. **Configure Amazon Simple Email Servie**
    - Verify the Email addresses you are going to use for sending the Email notifications as well as the recipient's Email address.
3. **Create a custom policy**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **Services > IAM**.
    2. In the left pane, click **Policies**.
    3. In the main pane, click **Create policy**.
    4. Click the **JSON** tab.
    5. Paste the [JSON code below](#JSON) into the text box.
    6. Click **Review policy**.
    7. On the **Review policy** page:
        - In the **Name** field, enter a name. Example: `FSS_SES_Send_Email_Policy`.
        - Click **Create policy**.
    8. Click the link to your policy to open its summary.
    9. Take note of the **Policy ARN** near the top of the page.
    </details>

    <details>
    <summary>Using the AWS CLI</summary>

    1. Paste the [JSON code below](#JSON) into a file called `fss-ses-send-email-policy.json` (or another name).
    2. In a shell program such as bash or Windows Powershell, enter the following AWS CLI command to create the policy:

        `aws iam create-policy --policy-name <YOUR_FSS_SES_SEND_EMAIL_POLICY> --policy-document file://fss-ses-send-email-policy.json`

        where `<YOUR_FSS_SES_SEND_EMAIL_POLICY>` is replaced with the name you want to give to the custom policy. Example: `FSS_SES_Send_Email_Policy`.
    3. In the output, take note of the custom policy's ARN. Example: `arn:aws:iam::0123456789012:policy/FSS_SES_Send_Email_Policy`
    </details>

    <details>
    <summary><a name="JSON">JSON code (for use in the custom policy)</a></summary>

    ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "ses:SendEmail",
                        "ses:SendRawEmail"
                    ],
                    "Resource": "*"
                }
            ]
        }
    ```

    </details>

4. **Create an execution role for the Lambda function**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **Services > IAM**.
    2. In the left pane, click **Roles**.
    3. In the main pane, click **Create role**.
    4. Under **Select type of trusted entity**:
        - Select the **AWS service** box.
        - Click the  **Lambda** service from the list.
        - Click **Next: Permissions**.
    5. In the search box:
        - Search for `AWSLambdaBasicExecutionRole`.
        - Select its check box.
        - Search for `<YOUR_FSS_SES_SEND_EMAIL_POLICY>` where `<YOUR_FSS_SES_SEND_EMAIL_POLICY>` is the name of your custom File Storage Security policy. Example: `FSS_SES_Send_Email_Policy`.
        - Select its check box in the list.
        - You now have two policies selected.
        - Click **Next: Tags**.
        - (Optional) Enter tags.
        - Click **Next: Review**.
    6. On the **Review** page:
        - In the **Role name** field, enter a name. Example: `FSS_Lambda_Email_Role`.
        - Make sure that two policies are listed.
        - Click **Create role**.
    </details>

   <details>
   <summary>Using the AWS CLI</summary>

    1. Enter the following AWS CLI command to create the role:

        `
        LAMBDA_TRUST="{
            \"Version\": \"2012-10-17\",
            \"Statement\": [
                {
                    \"Action\": \"sts:AssumeRole\",
                    \"Effect\": \"Allow\",
                    \"Principal\": {
                        \"Service\": \"lambda.amazonaws.com\"
                    }
                }
            ]
        }"
        `

        `aws iam create-role --role-name <YOUR_FSS_LAMBDA_EMAIL_ROLE> --assume-role-policy-document "${LAMBDA_TRUST}"`

        where `<YOUR_FSS_LAMBDA_EMAIL_ROLE>` is replaced with the name you want to give to the role. Example: `FSS_Lambda_Email_Role`.
    2. Attach the `AWSLambdaBasicExecutionRole` managed policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Email_Role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`

    3. Attach the custom policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Email_Role --policy-arn <YOUR_FSS_LAMBDA_EMAIL_POLICY_ARN>`

        where `<YOUR_FSS_LAMBDA_EMAIL_POLICY_ARN>` is replaced with the File Storage Security custom policy's ARN that you noted earlier. Example: `arn:aws:iam::0123456789012:policy/FSS_SES_Send_Email_Policy`.
    </details>

## Deploy the Lambda

<details>
<summary>Using the AWS console</summary>

1. In the main pane, click **Create function**.
    - Go to **Services > Lambda**.
    - Click **Create function**.
    - Select the **Author from scratch** box.
    - In the **Function name** field, enter a name. Example: `FSS_Scan_Send_Email`.
    - From the **Runtime** drop-down list, select **Python 3.8**.
    - Under **Permissions**, expand **Choose or create an execution role**.
    - Select **Use an existing role**.
    - In the drop-down list, select the execution role you created earlier. Example: `FSS_Lambda_Email_Role`.
    - Click **Create function** and leave the page open.
2. **Add function code**
    - Download the Lambda function [handler.py file from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-email-notification/handler.py).
    - On the AWS console page you left open, in the **Function code** section, remove the sample Lambda function code and paste the code from `handler.py`.
    - Click **Save** and leave the page open.
3. **Add environment variables**
    - Scroll to the **Environment variables** section.
    - Click **Edit** (on the right).
    - Click **Add environment variable**
        - In the **Key** field, enter `SENDER`
        - In the **Value** field, enter the Email address of the sender
    - Again, click **Add environment variable**
        - In the **Key** field, enter `RECIPIENT`
        - In the **Value** field, enter the Email address of the recepient
    - Again, click **Add environment variable**
        - In the **Key** field, enter `SUBJECT`
        - In the **Value** field, enter the Subjec for the Email. Example `CloudOne FSS Scan Result`
    - Click **Save** to save all three variables.
4. **Adjust timeout**
    -  Scroll to the **Basic settings** section.
    -  Click **Edit** (on the right).
    -  Set the **Timeout** to 30 sec.
    -  Click **Save** to save settings.

</details>

<details>
<summary>Using the AWS CLI</summary>

1. Download the Lambda function [handler.py file from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-email-notification/handler.py).
2. In a shell program, create a deployment package:

    `zip <YOUR_ZIP_NAME>.zip handler.py`

    where `<YOUR_ZIP_NAME>` is replaced with the name you want to give your Lambda function. Example: `scan-send-email`.
3. Create the Lambda function, using backslashes (`\`) to separate the lines, as shown below:

    ```bash
    aws lambda create-function --function-name <YOUR_FSS_SCAN_SEND_EMAIL> \
    --role <YOUR_FSS_LAMBDA_EMAIL_ROLE> \
    --runtime python3.8 \
    --timeout 30 \
    --memory-size 512 \
    --handler handler.lambda_handler \
    --zip-file fileb://<YOUR_ZIP_NAME>.zip \
    --region <YOUR_REGION>
    --environment Variables=\{SENDER=<YOUR_SENDER>,RECIPIENT=<YOUR_RECIPIENT>,SUBJECT="<YOUR_SUBJECT>"\}
    ```

- where:
    - `<YOUR_FSS_SCAN_SEND_EMAIL>` is replaced with the name you want to give your Lambda function. Example: `FSS_Scan_Send_Email`.
    - `<YOUR_FSS_LAMBDA_EMAIL_ROLE>` is replaced with the ARN of the role you previously created for the Lambda function. You can find the ARN in the AWS console under **Services > IAM > Roles** > your role > **Role ARN** field (at the top). Example: `arn:aws:iam::012345678901:role/FSS_Lambda_Email_Role`.
    - `<YOUR_ZIP_NAME>` is replaced with the name of the ZIP file you created earlier. Example: `scan-send-email`
    - `<YOUR_REGION>` is replaced by the region where the scanning bucket does reside in
    - `<YOUR_SENDER>` is replaced with the name of your sender Email address.
    - `<YOUR_RECIPIENT>` is replaced with the name of your recipient Email address.
    - `<YOUR_SUBJECT>`is replaced with the subject of your Email.
</details>

<details>
<summary>Using the Makefile</summary>

1. Download the [Makefile from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-email-notification/Makefile).
2. In a shell program, enter the following GNU Make command, using backslashes (`\`) to separate lines, as shown below:

    ```bash
    FUNCTION_NAME=<YOUR_FSS_SCAN_SEND_EMAIL> ROLE_ARN=<YOUR_FSS_LAMBDA_EMAIL_ROLE> \
    SENDER=<YOUR_SENDER> RECIPIENT=<YOUR_RECIPIENT> SUBJECT=<YOUR_SUBJECT> \
    make create-function
    ```
- where:
    - `<YOUR_FSS_SCAN_SEND_EMAIL>` is replaced with the name you want to give your Lambda function. Example: `FSS_Scan_Send_Email`.
    - `<YOUR_FSS_LAMBDA_EMAIL_ROLE>` is replaced with the ARN of the role you previously created for the Lambda function. You can find the ARN in the AWS console under **Services > IAM > Roles** > your role > **Role ARN** field (at the top). Example: `arn:aws:iam::012345678901:role/FSS_Lambda_Email_Role`.
    - `<YOUR_SENDER>` is replaced with the name of your sender Email address.
    - `<YOUR_RECIPIENT>` is replaced with the name of your recipient Email address.
    - `<YOUR_SUBJECT>`is replaced with the subject of your Email.
</details>

## Subscribe the Lambda to the SNS topic

<details>
<summary>Using the AWS console</summary>

1. Go to **Services > Lambda**.
2. Search for the Lambda function you created previously. Example: `FSS_Scan_Send_Email`
3. Click the link to your Lambda function to view its details.
4. Click **Add trigger** on the left.
5. From the **Trigger configuration** list, select **SNS**.
6. In the **SNS topic** field, enter the SNS topic ARN you found earlier.
7. Click **Add**. Your Lambda is now subscribed to the SNS topic.

</details>

<details>
<summary>Using the AWS CLI</summary>

1. **Find the 'ScanResultTopic' SNS topic ARN** 
    - In the AWS console, go to **Services > CloudFormation** > your all-in-one stack > **Resources** > your storage stack > **Resources**.
    - Scroll down to locate the  **ScanResultTopic** Logical ID. 
    - Copy the **ScanResultTopic** ARN to a temporary location. Example: `arn:aws:sns:us-east-1:123445678901:FileStorageSecurity-All-In-One-Stack-StorageStack-1IDPU1PZ2W5RN-ScanResultTopic-N8DD2JH1GRKF`
2. **Find the Lambda function ARN**
    
    📌 The Lamdba function ARN is required only if you plan to use the AWS CLI (as opposed to the console) to subscribe the Lambda to the SNS topic.
    - In the AWS console, go to **Services > Lambda**.
    - Search for the Lambda function you created previously. Example: `FSS_Scan_Send_Email`
    - Click the Lambda function link.
    - On the top-left, locate the **ARN**.
    - Copy the ARN to a temporary location. Example: `arn:aws:lambda:us-east-1:123445678901:function:FSS_Scan_Send_Email`
    - Enter the following AWS CLI command to subscribe your Lamdba function to the SNS topic:
        
        `aws sns subscribe --topic-arn <SNS_TOPIC_ARN> --protocol lambda --notification-endpoint <YOUR_LAMBDA_FUNCTION_ARN> --region <YOUR_REGION>`
    - where:
        - `<SNS_TOPIC_ARN>` is replaced with the SNS topic ARN you found earlier.
        - `<YOUR_LAMBDA_FUNCTION_ARN>` is replaced with the Lambda function ARN you found earlier.
        - `<YOUR_REGION>` is replaced by the region where the scanning bucket does reside in
    - Lastly, grant the SNS service permission to invoke your function.

        `aws lambda add-permission --function-name <FUNCTION_NAME> --region <YOUR_REGION> --statement-id sns --action lambda:InvokeFunction --principal sns.amazonaws.com --source-arn <SNS_TOPIC_ARN>`
    - where:
        - `<FUNCTION_NAME>` is replaced by the name of the Lambda function you created previously. Example: `FSS_Scan_Send_Email`
        - `<YOUR_REGION>` is replaced by the region where the scanning bucket does reside in
        - `<SNS_TOPIC_ARN>` is replaced with the SNS topic ARN you found earlier.

</details>
