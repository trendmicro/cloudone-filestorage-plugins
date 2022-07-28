# Cloud One File Storage Security Post Scan Action for GCP - MS Teams notifications

**:warning: Note: File Storage Security for GCP solution is in preview.**

## Prerequisites

1. **Install supporting tools**
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk)

## Installation

### With GCP Cloud Shell

1. Open in Cloud Shell

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Ftrendmicro%2Fcloudone-filestorage-plugins.git&cloudshell_workspace=post-scan-actions%2Fgcp-python-teams-notification&cloudshell_tutorial=docs/deploy-tutorial.md)

### Local Machine

1. Login to the Google Cloud SDK

   ```sh
   gcloud init
   ```

   (or)

   ```sh
   gcloud auth application-default login
   ```

2. Set the GCP Project ID on the CLI where the storage stack is deployed.

   ```
   gcloud config set project <PROJECT_ID>
   ```

## Configure Google Cloud function

1. Specify the following fields and execute the deployment script:

- **TEAMS_URL** - The incoming webhook URL generated from MS Teams Channel connectors. This generated URL can be created by following the step-by-step guide to creating an Incoming Webhook described here - [How to configure and use Incoming Webhooks in Microsoft Teams](https://techcommunity.microsoft.com/t5/microsoft-365-pnp-blog/how-to-configure-and-use-incoming-webhooks-in-microsoft-teams/ba-p/2051118).
- **DEPLOYMENT_REGION** - The region where the File Storage Security Storage stack was deployed.
- **GCP_PROJECT_ID** - Project ID of the GCP project.
- **TRIGGER_RESOURCE** - Topic name of the scan result topic name. Example: `projects/<PROJECT_ID>/topics/<SCAN_RESULT_TOPIC_NAME>`
- **EVENT_TYPE** - Optional. Defaults to `providers/cloud.pubsub/eventTypes/topic.publish`

## Deploy Google Cloud function to push Slack notifications

1. Install Serverless on your local machine.

   ```sh
   npm install -g serverless
   ```

2. Deploy Serverless project.

   ```sh
   serverless plugin install -n serverless-google-cloudfunctions

   serverless deploy -s prod /
   --param="TEAMS_URL=<TEAMS_URL>" /
   --param="DEPLOYMENT_REGION=<DEPLOYMENT_REGION>" /
   --param="GCP_PROJECT_ID=<GCP_PROJECT_ID>" /
   --param="TRIGGER_RESOURCE=<TRIGGER_RESOURCE>" /
   --param="EVENT_TYPE=<EVENT_TYPE>"
   ```

## Test MS Teams notifications

Check MS Teams to see new notifications. To test your deployment, you'll need to generate a malware detection using the eicar file.

1. Download the eicar file from eicar file page into your scanning bucket with the script.

    ```
    wget https://secure.eicar.org/eicar.com.txt

    gsutil cp eicar.com.txt gs://<SCANNING_BUCKET_NAME>/eicar
    ```

   > File Storage Security scans the file and detects the malware.

2. Execute the script to examine the scan result:

    ```
    gsutil stat 'gs://<SCANNING_BUCKET_NAME>/eicar'
    ```

   - In Metadata, look for the following tags:
      * **fss-scan-date**: date_and_time
      * **fss-scan-result**: malicious
      * **fss-scanned**: true

The tags indicate that File Storage Security scanned the file and tagged it as malware. The scan results are also available in the console on the Scan Activity page.

If all the steps were successful, you should get a MS Teams Channel notification on the configured MS Teams Channel.
