# Deploy to All Existing Azure Resource
This script will deploy File Storage Security Stack to all storage accounts unless defined in `exclude.txt` text file. After deployment, the stacks will be registered with the Cloud One Console. 

**Before you deploy**

   * Obtain your Cloud One API Key
      - Generate API Key: [Cloud One API Key](https://cloudone.trendmicro.com/docs/account-and-user-management/c1-api-key/)

<hr>

**1. Clone Repo**
 - Clone this repository `git clone https://github.com/trendmicro/cloudone-community.git`
 - After cloning repo:
```
   cd .\cloudone-community\File-Storage-Security/Deployment/azure-python-deploy-to-all-existing-Azure   
```

**2. Configure the Exclusions text file `exclude.txt`**
   * Create a new file called `exclude.txt` with names of Azure storage accounts to exclude from FSS deployment.
   - 1 per line, Example: [exclude.txt](https://github.com/trendmicro/cloudone-community/blob/main/File-Storage-Security/Deployment/python-deploy-to-all-existing/exclude.txt)
   * For organizations with a large number of storage accounts, a list of Azure storage accounts can be piped into `exclude.txt` using `azure-cli` or `PowerShell`:
   ```
   # Bash
   az storage account list --query "[?tags.AutoDeployFSS != 'True'].name" --output tsv > exclude.txt
   cat exclude.txt

   # PowerShell
   Clear-Content -Path exclude.txt
   Get-AzStorageAccount |  Where-Object {$_.tags.AutoDeployFSS -ne 'True'} | Select-Object -Property StorageAccountName | ConvertTo-JSON | Out-File -FilePath exclude.json
   $json = (Get-Content "exclude.json" -Raw) | ConvertFrom-Json
   foreach($v in $json.StorageAccountName) {
      Write-Output "${v}" >> exclude.txt
   }
   more exclude.txt
   ```
**3. Configuration file**

* Complete the `config.json` configuration file with valid input.

| Fields | Environment Variable | Type | Description | Required? |
|--------| ---- | ----------- | --------- | --------- |
| `app_id` | | String | Azure Application ID | Yes |
| `tenant_id` | | String | Azure Tenant ID | Yes |
| `subscription_id` | AZURE_SUBSCRIPTION_ID | String | Azure Subscription ID | Yes |
| `keyvault_uri` | | String | Azure KeyVault URI | Yes |
|`cloudone.region` | CLOUDONE_REGION | String | Cloud One Region Example: us-1 or ca-1 | Yes |
| `cloudone.api_key` | CLOUDONE_API_KEY | String | Cloud One File Storage Security API Key. You can create an API Key using these instructions - https://cloudone.trendmicro.com/docs/workload-security/api-cookbook-set-up/#create-an-api-key | Yes |
| `cloudone.max_storage_stack_per_scanner_stack` | MAX_STORAGE_STACK_PER_SCANNER_STACK | Number | Recommended to set to 50, i.e, for every 50 Storage stacks, 1 Scanner stack would be created. Contact the product team for your usecase requirements. | Yes |
| `azure_creds.key` | | Boolean | Azure Credentials Client Value | Yes |
| `azure_creds.secret` | | String | Azure Credentials Secret Value | Yes  |

**4. Deploy Tool via the Serverless Framework**
* Open terminal/cmd:
   ```
      serverless deploy -s dev
   ```

# Additional Notes

### Tags

The Script will choose whether or not to deploy a storage stack depending on a storage accounts' tags. **See below for details**:

| Tag             | Value                 | Behavior                                                      |
| --------------  | --------------------- |-------------------------------------------------------------- |
| [no tag]        | [none]                | No action                                                     |
| `AutoDeployFSS` | `True`                | Storage Stack and Scanner Stack will be deployed              |
| `AutoDeployFSS` | `(any other value)`   | Skip                                                          |
| `FSSMonitored`  | `yes`                 | Storage Stack Already Exists, Scanner Stack associated (skip) |
| `FSSMonitored`  | `(any other value)`   | Skip                                                          |

### Supported FSS regions

Please note this script deploys Scanner Stacks to select Azure locations as listed in the supported document here - [What Azure services and regions are supported?](https://cloudone.trendmicro.com/docs/file-storage-security/supported-azure/). Storage Stacks that are not present in the same Azure locations will be mapped to Scanner Stacks deployed in the same geographyGroup as defined by Azure. Any data transfer cost(s) incurred in this data transfer would be your responsibility.
