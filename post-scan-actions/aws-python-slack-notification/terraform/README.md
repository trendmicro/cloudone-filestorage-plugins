# Post Scan Action - Slack Notification

After a scan occurs and a malicious file is detected, this example Lambda function sends out a notification to Slack using Amazon Simple Notification Service.

## Prerequisites

1. **Install supporting tools**
    Do one of the following:
    - Install the AWS command line interface (CLI). See [Installing the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) for details.
    - Install Terraform CLI. See [Install Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli#install-terraform) for download information.
2. **Configure Slack Webhook App**
    - Create a Slack Channel to receive the notification
    - Go to App Directory > Search `Incoming WebHooks`.
    - Click on `Incoming WebHooks`, then click "Add to Slack"
    - Choose the Channel to receive the notification
    - Copy Webhook URL
    - Enter the Description of your WebHook.
    - Enter the Name of the Slack WebHook, by default it will use `incoming-webhook`; if you prefer, you can customize the name.
    - If you want any custom icon to add that in Customize Icon section.
    - Click "Save Setting"
    
    [Additional information](https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack)

3. Make sure that you have terraform and AWS CLI installed and configured, then go to terraform folder and change appropriately the values at the variables in the `variables.tf` file.

    Then you can execute the following:

    ```terraform
        terraform init
        terraform plan
        terraform apply
    ```

## Clean-up

In case you want to revert/destroy the resources created, execute the following:

```terraform
terraform destroy
```