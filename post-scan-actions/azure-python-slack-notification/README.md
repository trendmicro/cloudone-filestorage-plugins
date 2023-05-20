# Cloud One File Storage Security Post Scan Action for Azure Storage Account - Slack Notification

After a malicious scan result, this example Azure function sends a notification to a Slack channel.

## Prerequisites

1. **Install supporting tools**
    - Install the Azure command line interface (CLI). See [Install the Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) for details.
    - Install the Azure Functions Core Tools. See [Work with Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) for details.
1. **Find the Service Bus Topic Resource ID**
    - In the Azure portal, go to **Resource group** > your storage stack > **Deployments > storageStack > Outputs**.
    - Copy the value of **scanResultTopicResourceID** to a temporary location. Example: `/subscriptions/12345678-1111-1111-1111-123456789012/resourceGroups/my-storage-stack/providers/Microsoft.ServiceBus/namespaces/tmsrt0abcd56789abcd/topics/scan-result-topic`.
1. **Configure Slack Webhook App**
    - Create a Slack Channel to receive the notification
    - Go to App Directory > Search `Incoming WebHooks`.
    - Click on `Incoming WebHooks`, then click "Add to Slack"
    - Choose the Channel to receive the notification
    - Copy Webhook URL
    - Enter the Description of your WebHook.
    - Enter the Name of the Slack WebHook, by default it will use `incoming-webhook`; if you prefer, you can customize the name.
    - If you want any custom icon to add that in Customize Icon section.
    - Click "Save Setting"
    - [Additional information](https://slack.com/help/articles/115005265063-Incoming-webhooks-for-Slack)

## Installation

### Deploy Azure function app

1. Log in to the Azure CLI and switch to the Azure subscription to deploy resources:

    ```bash
    az login
    az account set -s $AZURE_SUBSCRIPTION_NAME
    ```

1. Prepare a resource group for deploying the resources. To create a new resource group, execute the following command:

    ```bash
    az group create -n $RESOURCE_GROUP_NAME -l $AZURE_REGION
    ```

1. Deploy the function app and required resources:

    ```bash
    az deployment group create \
        --name fss-slack-notification-deployment \
        --resource-group $RESOURCE_GROUP_NAME \
        --template-uri https://raw.githubusercontent.com/trendmicro/cloudone-filestorage-plugins/master/post-scan-actions/azure-python-slack-notification/template.json \
        -p fssSlackFunctionName=$FUNCTION_NAME \
        slackWebHookURL=$SLACK_WEBHOOK_URL \
        slackChannelName=$SLACK_CHANNEL_NAME \
        scanResultTopicResourceID=$SCAN_RESULT_TOPIC_RESOURCE_ID
    ```

## Test the function

Follow [Generate your first detection on Azure](https://cloudone.trendmicro.com/docs/file-storage-security/gs-generate-detection-azure/) to generate a malware detection in the scanning blob storage account.

> **NOTE:** It can take about 15-30 seconds or more for the notification.
