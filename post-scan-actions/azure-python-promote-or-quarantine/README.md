# Cloud One File Storage Security Post Scan Action for Azure Storage Account - Promote or Quarantine

After a scan occurs, this example Azure function places clean files in one storage account and malicious files in another.

## Prerequisites

1. **Install supporting tools**
    - Install the Azure command line interface (CLI). See [Install the Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) for details.
    - Install the Azure Functions Core Tools. See [Work with Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) for details.
1. **Create Azure storage accounts and connection strings**
    - Create a 'Promote storage account' to receive clean files. Example: `fsspromote`.
    - In the Azure portal, go to **Storage account** > Promote storage account > **Access keys**, click **Show keys**, and copy the value of **Connection string** of either key.
    - Create a 'Quarantine storage account' to receive quarantined files. Example: `fssquarantine`.
    - In the Azure portal, go to **Storage account** > Quarantine storage account > **Access keys**, click **Show keys**, and copy the value of **Connection string** of either key.
1. **Find the scanning blob storage account resource ID and the service bus topic resource ID**
    - In the Azure portal, go to **Resource group** > your storage stack > **Deployments > storageStack > Outputs**.
    - Copy the value of **blobStorageAccountResourceID** to a temporary location. Example: `/subscriptions/12345678-1111-1111-1111-123456789012/resourceGroups/my-storages/providers/Microsoft.Storage/storageAccounts/scanningstorage`.
    - Copy the value of **scanResultTopicResourceID** to a temporary location. Example: `/subscriptions/12345678-1111-1111-1111-123456789012/resourceGroups/my-storage-stack/providers/Microsoft.ServiceBus/namespaces/tmsrt0abcd56789abcd/topics/scan-result-topic`.

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
        --name fss-promote-or-quarantine-plugin-deployment \
        --resource-group $RESOURCE_GROUP_NAME \
        --template-uri https://raw.githubusercontent.com/trendmicro/cloudone-filestorage-plugins/master/post-scan-actions/azure-python-promote-or-quarantine/template.json \
        -p promoteOrQuarantineFunctionName=$FUNCTION_NAME \
        scanningStorageAccountResourceID=$BLOB_STORAGE_ACCOUNT_RESOURCE_ID \
        scanResultTopicResourceID=$SCAN_RESULT_TOPIC_RESOURCE_ID \
        promoteStorageAccountConnectionString="$PROMOTE_STORAGE_ACCOUNT_CONNECTION_STRING" \
        promoteMode=move \
        quarantineStorageAccountConnectionString="$QUARANTINE_STORAGE_ACCOUNT_CONNECTION_STRING" \
        quarantineMode=move
    ```

    To copy the scanned files from the scanning storage account to the promote or quarantine storage account instead of moving them, modify the value of `promoteMode` or `quarantineMode` parameter to `copy`:

    ``` bash
    promoteMode=copy
    quarantineMode=copy
    ```

### 2. Publish Azure function

1. Download [cloudone-filestorage-plugins repository](https://github.com/trendmicro/cloudone-filestorage-plugins/tree/master)
1. Navigate to `post-scan-actions/azure-python-promote-or-quarantine/promoteOrQuarantineFunction`
1. Publish the function to the function app:

    ```bash
    func azure functionapp publish $FUNCTION_NAME --python
    ```

## Test the function

Follow [Generate your first detection on Azure](https://cloudone.trendmicro.com/docs/file-storage-security/gs-generate-detection-azure/) to generate a malware detection in the scanning blob storage account.

> **NOTE:** It can take about 15-30 seconds or more for the file to move.
