# Cloud One File Storage Security Post Scan Action for Azure Storage Account - MS Teams Notification

After a malicious scan result, this example Azure function sends a notification to a MS Teams channel.

## Prerequisites

1. **Install supporting tools**
    - Install the Azure command line interface (CLI). See [Install the Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) for details.
    - Install the Azure Functions Core Tools. See [Work with Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) for details.
1. **Find the Service Bus Topic Resource ID**
    - In the Azure portal, go to **Resource group** > your storage stack > **Deployments > storageStack > Outputs**.
    - Copy the value of **scanResultTopicResourceID** to a temporary location. Example: `/subscriptions/12345678-1111-1111-1111-123456789012/resourceGroups/my-storage-stack/providers/Microsoft.ServiceBus/namespaces/tmsrt0abcd56789abcd/topics/scan-result-topic`.
1. **Configure Microsoft Teams Webhook Connector**
    - Create a channel for a team to receive the notification
    - Click the `...` ellipsis next to the team channel.
    - Click `Connectors`.
    - Click `Incoming Webhooks`.
    - Click `Configure`
    - Create a name for the Teams WebHook, ex 'TM-FSS'
    - Click `Create`
    - Copy the Webhook URL 
    
    [Additional information](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)

## Installation

### 1. Deploy Azure function app

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
        --name fss-teams-notification-deployment \
        --resource-group $RESOURCE_GROUP_NAME \
        --template-uri https://raw.githubusercontent.com/trendmicro/cloudone-filestorage-plugins/master/post-scan-actions/azure-python-teams-notification/template.json \
        -p fssTeamsFunctionName=$FUNCTION_NAME \
        teamsWebHookURL=$TEAMS_WEBHOOK_URL \
        scanResultTopicResourceID=$SCAN_RESULT_TOPIC_RESOURCE_ID
    ```

### 2. Publish Azure function

1. Download [cloudone-filestorage-plugins repository](https://github.com/trendmicro/cloudone-filestorage-plugins/tree/master)
1. Navigate to `post-scan-actions/azure-python-teams-notification/teamsNotification`
1. Publish the function to the function app:

    ```bash
    func azure functionapp publish $FUNCTION_NAME --python
    ```

## Test the function

Follow [Generate your first detection on Azure](https://cloudone.trendmicro.com/docs/file-storage-security/gs-generate-detection-azure/) to generate a malware detection in the scanning blob storage account.

> **NOTE:** It can take about 15-30 seconds or more for the notification.
