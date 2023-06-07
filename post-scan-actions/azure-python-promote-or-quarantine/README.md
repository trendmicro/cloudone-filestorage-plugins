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
1. **[VNet only]Set up VNet-related resources**
    - Refer to the documentation on [Deploying in Azure VNet](https://cloudone.trendmicro.com/docs/file-storage-security/azure-vnet-deployment/) to prepare a VNet environment.
    - Ensure that the 'Promote storage account' and 'Quarantine storage account' created in step 2 can be accessed via the VNet.

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

### Deploy Function App with VNet Integration

If you want to deploy Promote or Quarantine Plugin in Azure VNet, ensure that you have reviewed the documentation on how to [deploy the Azure Stack to VNet](https://cloudone.trendmicro.com/docs/file-storage-security/azure-vnet-deployment/). Follow the steps below to deploy the Promote or Quarantine plugin with VNet integration:

1. Create a new subnet for the Promote or Quarantine plugin function app integration using the following command:

    ```bash
    az network vnet subnet create \
        --name $PROMOTE_OR_QUARANTINE_SUBNET_NAME \
        --resource-group $RESOURCE_GROUP_NAME \
        --vnet-name $VNET_NAME \
        --address-prefixes $ADDRESS_PREFIX \
        --delegations Microsoft.Web/serverFarms
    ```

    Additionally, you need a subnet for the private endpoint to access the private resources. You can use the existing Private Endpoints Subnet in Azure Stack or create a new subnet. Ensure that the subnet has the necessary permissions to access the Azure Stack resources.

    ```bash
    az network vnet subnet create \
        --name $PRIVATE_ENDPOINT_SUBNET_NAME \
        --resource-group $RESOURCE_GROUP_NAME \
        --vnet-name $VNET_NAME \
        --address-prefixes $ADDRESS_PREFIX
    ```

1. To allow access to the `Protected storage account`, `Promote storage account`, and `Quarantine storage account` from the Azure Stack's network, you need to enable access through a [Private Endpoint](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview) or a [Service Endpoint](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-service-endpoints-overview).

1. If you are using an Azure firewall, add the following firewall rule to ensure that the Function App can access the artifacts from Github:

    | Name | Source Type | Source | Protocol:Port | Target FQDNs |
    | --- | --- | --- | --- | --- |
    | Github | IP address | &lt;promote-or-quarantine-subnet&gt; | https:443 | github.com |
    | Github Content | IP address | &lt;promote-or-quarantine-subnet&gt; | https:443 | objects.githubusercontent.com |

1. Deploy the function app and the required resources using the following command:

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
        quarantineMode=move \
        VNETResourceID="$VNET_RESOURCE_ID" \
        VNETPromoteOrQuarantineSubnetName=$PROMOTE_OR_QUARANTINE_SUBNET_NAME \
        VNETPrivateEndpointsSubnetName=$PRIVATE_ENDPOINT_SUBNET_NAME \
        VNETFilePrivateDNSZoneResourceID="$FILE_PRIVATE_DNS_ZONE_RESOURCE_ID" \
        VNETBlobPrivateDNSZoneResourceID="$BLOB_PRIVATE_DNS_ZONE_RESOURCE_ID" \
        VNETRestrictedAccessForApplicationInsights=true|false \
    ```

    Set the `VNETRestrictedAccessForApplicationInsights` parameter to `true` if you want to log via the private network. Otherwise, leave it as `false`.

1. If you are using Azure Monitor Private Link Scopes(AMPLS) with VNet, which means you have set the `VNETRestrictedAccessForApplicationInsights` parameter to `true` in the previous step, you should add the application insight to AMPLS using the following command. The APPLICATION_INSIGHT_RESOURCE_ID can be found in the deployment output `applicationInsightResourceID`.

    ```bash
    az monitor private-link-scope scoped-resource create \
        --linked-resource $APPLICATION_INSIGHT_RESOURCE_ID \
        --name $SCOPED_RESOURCE_NAME \
        --resource-group $AMPLS_RESOURCE_GROUP \
        --scope-name $AMPLS_NAME
    ```

## Test the function

Follow [Generate your first detection on Azure](https://cloudone.trendmicro.com/docs/file-storage-security/gs-generate-detection-azure/) to generate a malware detection in the scanning blob storage account.

> **NOTE:** It can take about 15-30 seconds or more for the file to move.
