# Post Scan Action - MS Teams Notification

After a scan occurs and a malicious file is detected, this example Lambda function sends out a notification to Microsoft Teams using Amazon Simple Notification Service.

## Prerequisites

1. **Install supporting tools**
    Do one of the following:
        - Install the AWS command line interface (CLI). See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.
        - Install GNU Make. See [GNU Make](https://www.gnu.org/software/make/) for download information.
2. **Configure Microsoft Teams Webhook Connector**
    - Create a channel for a team.
    - Click the **...** ellipsis next to the team name.
    - Click **Connectors**.
    - Search `Incoming WebHooks`
    - Click **Configure**.
    - Create a name for the Teams WebHook, ex 'TM-FSS'
    - Click **Create**.
    - Copy the Webhook URL.

    [Additional information](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)

3. **Create an execution role for the Lambda function**

    <details>
    <summary>Using the AWS console</summary>

    1. Go to **Services > IAM**.
    2. In the left pane, click **Roles**.
    3. In the main pane, click the **Create role** button.
    4. Under **Select type of trusted entity**:
        - Select the **AWS service** box.
        - Click the  **Lambda** service from the list.
        - Click **Next: Permissions**.
    5. In the search box:
        - Search for `AWSLambdaBasicExecutionRole`.
        - Select its check box.

        - You now have two policies selected.
        - Click **Next: Tags**.
        - (Optional) Enter tags.
        - Click **Next: Review**.
    6. On the **Review** page:
        - In the **Role name** field, enter a name. Example: `FSS_Lambda_Teams_Notification_Role`.
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

        `aws iam create-role --role-name <YOUR_FSS_LAMBDA_TEAMS_NOTIFICATION_ROLE> --assume-role-policy-document "${LAMBDA_TRUST}"`

        where `<YOUR_FSS_LAMBDA_TEAMS_NOTIFICATION_ROLE>` is replaced with the name you want to give to the role. Example: `FSS_Lambda_Teams_Notification_Role`.
    2. Attach the `AWSLambdaBasicExecutionRole` managed policy to the role:

        `aws iam attach-role-policy --role-name FSS_Lambda_Teams_Notification_Role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`
    </details>

## Deploy the Lambda

<details>
<summary>Using the AWS console</summary>

1. **Create function**
    - Go to **Services > Lambda**.
    - Click the **Create function** button.
    - Select the **Author from scratch** box.
    - In the **Function name** field, enter a name. Example: `FSS_Scan_Send_Teams_Notification`.
    - From the **Runtime** drop-down list, select **Python 3.12**.
    - Under **Permissions**, expand **Change default execution role.**
    - Select **Use an existing role**.
    - In the drop-down list, select the execution role you created earlier. Example: `FSS_Lambda_Teams_Notification_Role`.
    - Click **Create function** and leave the page open.
2. **Add function code**
    - Download the Lambda function [handler.py file from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-teams-notification/handler.py).
    - On the AWS console page you left open, in the **Function code** section, remove the sample Lambda function code and paste the code from `handler.py`.
    - Click **Save** and leave the page open.
3. **Add environment variables**
    - Scroll to the **Environment variables** section.
    - Click **Edit** (on the right).
    - Click **Add environment variable**
        - In the **Key** field, enter `TEAMS_URL`
        - In the **Value** field, enter the incoming webhook URL that you created to receive the notification
    - Click **Save** to save all variables.
4. **Adjust timeout**
    -  Scroll to the **Basic settings** section.
    -  Click **Edit** (on the right).
    -  Set the **Timeout** to 30 sec.
    -  Click **Save** to save settings.

</details>

<details>
<summary>Using the AWS CLI</summary>

1. Download the Lambda function [handler.py file from GitHub](https://github.com/trendmicro/cloudone-filestorage-plugins/blob/master/post-scan-actions/aws-python-teams-notification/handler.py).
2. In a shell program, create a deployment package:

    `zip <YOUR_ZIP_NAME>.zip handler.py`

    where `<YOUR_ZIP_NAME>` is replaced with the name you want to give your Lambda function. Example: `scan-send-teams-notification`.
3. Create the Lambda function, using backslashes (`\`) to separate the lines, as shown below:

    ```bash
    aws lambda create-function --function-name <YOUR_FSS_SCAN_SEND_TEAMS_NOTIFICATION> \
    --role <YOUR_FSS_LAMBDA_TEAMS_NOTIFICATION_ROLE> \
    --runtime python3.12 \
    --timeout 30 \
    --memory-size 512 \
    --handler handler.lambda_handler \
    --zip-file fileb://<YOUR_ZIP_NAME>.zip \
    --region <YOUR_REGION>
    --environment Variables=\{TEAMS_URL=<YOUR_TEAMS_URL>\}
    ```

- where:
    - `<YOUR_FSS_SCAN_SEND_TEAMS_NOTIFICATION>` is replaced with the name you want to give your Lambda function. Example: `FSS_Scan_Send_Teams_Notification`.
    - `<YOUR_FSS_LAMBDA_TEAMS_NOTIFICATION_ROLE>` is replaced with the ARN of the role you previously created for the Lambda function. You can find the ARN in the AWS console under **Services > IAM > Roles** > your role > **Role ARN** field (at the top). Example: `arn:aws:iam::000000000000:role/FSS_Lambda_Teams_Notification_Role`.
    - `<YOUR_ZIP_NAME>` is replaced with the name of the ZIP file you created earlier. Example: `scan-send-teams-notification`
    - `<YOUR_REGION>` is replaced by the region where the scanning bucket resides
    - `<YOUR_TEAMS_URL>` is replaced with the name of your incomming webhook MSTEAMS URL.
</details>

## Subscribe the Lambda to the SNS topic

<details>
<summary>Using the AWS console</summary>

1. Go to **Services > Lambda**.
2. Search for the Lambda function you created previously. Example: `FSS_Scan_Send_Teams_Notification`
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
    - Copy the **ScanResultTopic** ARN to a temporary location. Example: `arn:aws:sns:us-east-1:000000000000:FileStorageSecurity-All-In-One-Stack-StorageStack-1IDPU1PZ2W5RN-ScanResultTopic-N8DD2JH1GRKF`
2. **Find the Lambda function ARN**

    📌 The Lamdba function ARN is required only if you plan to use the AWS CLI (as opposed to the console) to subscribe the Lambda to the SNS topic.
    - In the AWS console, go to **Services > Lambda**.
    - Search for the Lambda function you created previously. Example: `FSS_Scan_Send_Teams_Notification`
    - Click the Lambda function link.
    - On the top-left, locate the **ARN**.
    - Copy the ARN to a temporary location. Example: `arn:aws:lambda:us-east-1:000000000000:function:FSS_Scan_Send_Teams_Notification`
    - Enter the following AWS CLI command to subscribe your Lamdba function to the SNS topic:

        `aws sns subscribe --topic-arn <SNS_TOPIC_ARN> --protocol lambda --notification-endpoint <YOUR_LAMBDA_FUNCTION_ARN> --region <YOUR_REGION>`
    - where:
        - `<SNS_TOPIC_ARN>` is replaced with the SNS topic ARN you found earlier.
        - `<YOUR_LAMBDA_FUNCTION_ARN>` is replaced with the Lambda function ARN you found earlier.
        - `<YOUR_REGION>` is replaced by the region where the scanning bucket resides
    - Lastly, grant the SNS service permission to invoke your function.

        `aws lambda add-permission --function-name <FUNCTION_NAME> --region <YOUR_REGION> --statement-id sns --action lambda:InvokeFunction --principal sns.amazonaws.com --source-arn <SNS_TOPIC_ARN>`
    - where:
        - `<FUNCTION_NAME>` is replaced by the name of the Lambda function you created previously. Example: `FSS_Scan_Send_Teams_Notification`
        - `<YOUR_REGION>` is replaced by the region where the scanning bucket resides
        - `<SNS_TOPIC_ARN>` is replaced with the SNS topic ARN you found earlier.

</details>
