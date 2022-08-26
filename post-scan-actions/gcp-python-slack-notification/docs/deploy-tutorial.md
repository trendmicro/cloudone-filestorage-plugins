# Cloud One File Storage Security Post Scan Action for  Slack notifications

## Overview

<walkthrough-tutorial-duration duration="10"></walkthrough-tutorial-duration>

This tutorial will guide you to deploy a Google Cloud function to push Slack notifications for every File Storage Security detection.

--------------------------------

## Project Setup

Select the project in which you want to deploy the slack notification Cloud function. Ideally, this would be the same project where the Cloud Storage bucket and File Storage Security Storage stack reside.

<walkthrough-project-setup></walkthrough-project-setup>

Copy and execute the script in the Cloud Shell:

```
gcloud config set project <walkthrough-project-id/>
```

--------------------------------

## Configure Google Cloud function

Build your deployment command by substituting the following fields in your sample deployment command. An example/default value for these fields can be found in the field description below.

### Deployment by command-line

Replace the values in the following command and store the output for the next step

```sh
    serverless deploy -s prod \
    --param="SLACK_URL=<SLACK_URL>" \
    --param="DEPLOYMENT_REGION=<DEPLOYMENT_REGION>" \
    --param="GCP_PROJECT_ID=<GCP_PROJECT_ID>" \
    --param="TRIGGER_RESOURCE=<TRIGGER_RESOURCE>" \
    --param="EVENT_TYPE=<EVENT_TYPE>" \
    --param="SLACK_CHANNEL=<SLACK_CHANNEL>" \
    --param="SLACK_USERNAME=<SLACK_USERNAME>"
```

where,

- **SLACK_URL** - The incoming webhook URL generated from Slack Apps. Example: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`
- **DEPLOYMENT_REGION** - The region where the File Storage Security Storage stack was deployed.
- **GCP_PROJECT_ID** - Project ID of the GCP project.
- **TRIGGER_RESOURCE** - Topic name of the scan result topic name. Example: `projects/<PROJECT_ID>/topics/<SCAN_RESULT_TOPIC_NAME>`
- **EVENT_TYPE** - Optional. Defaults to `providers/cloud.pubsub/eventTypes/topic.publish`
- **SLACK_CHANNEL** - Optional. Defaults to ***#notifications*** Slack channel
- **SLACK_USERNAME** - Optional. Defaults to "*Cloud One File Storage Security*"

### Deployment through serverless.yml file

You could hardcode these values in the <walkthrough-editor-open-file filePath="cloudone-filestorage-plugins/post-scan-actions/gcp-python-slack-notification/serverless.yml">serverless.yml</walkthrough-editor-open-file> file. To override a hard-coded value during runtime, simply pass it as a `--param` as shown in the command-line section above.

Simply replace, the `params` section of the serverless.yml with the right values and run `serverless deploy` as shown in the next step.

```yaml
params:
  prod:
    SLACK_URL: <SLACK_URL>
    SLACK_CHANNEL: notifications
    SLACK_USERNAME: Cloud One File Storage Security
    DEPLOYMENT_REGION: <GCP_DEPLOYMENT_REGION>
    GCP_PROJECT_ID: <PROJECT_ID>
    EVENT_TYPE: providers/cloud.pubsub/eventTypes/topic.publish
    TRIGGER_RESOURCE: projects/<PROJECT_ID>/topics/<SCAN_RESULT_TOPIC_NAME>
```

--------------------------------

## Deploy Google Cloud function to push Slack notifications

1. Install Serverless on your local machine.

    ```sh
    npm install -g serverless
    ```

2. Deploy Serverless project.

    This cloudone plugin requires some dependencies from the serverless plugin ecosystem, like `serverless-google-cloudfunctions` before we can deploy this project.

    - Install serverless dependencies

        ```sh
        serverless plugin install -n serverless-google-cloudfunctions
        ```

    - Deploy your serverless project

        - Through command-line

            ```sh
            serverless deploy -s prod \
            --param="SLACK_URL=<SLACK_URL>" \
            --param="DEPLOYMENT_REGION=<DEPLOYMENT_REGION>" \
            --param="GCP_PROJECT_ID=<GCP_PROJECT_ID>" \
            --param="TRIGGER_RESOURCE=<TRIGGER_RESOURCE>" \
            --param="EVENT_TYPE=<EVENT_TYPE>" \
            --param="SLACK_CHANNEL=<SLACK_CHANNEL>" \
            --param="SLACK_USERNAME=<SLACK_USERNAME>"
            ```

        - Using `serverless.yml` and the values provided within the file

            ```sh
            serverless deploy -s prod
            ```

--------------------------------

## Test Slack notifications

Check Slack to see new notifications. To test your deployment, you'll need to generate a malware detection using the eicar file.

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

If all the steps were successful, you should get a Slack notification on the <SLACK_CHANNEL> specified.

--------------------------------
