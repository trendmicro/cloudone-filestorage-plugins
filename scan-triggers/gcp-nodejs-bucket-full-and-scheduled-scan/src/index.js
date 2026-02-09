// Copyright (C) 2024 Trend Micro Inc. All rights reserved.

const { PubSub } = require('@google-cloud/pubsub');
const { Storage } = require('@google-cloud/storage');
const functions = require('@google-cloud/functions-framework');

const fs = require('fs');

const scannerQueueTopic = process.env.SCANNER_PUBSUB_TOPIC;
const scannerProjectID = process.env.SCANNER_PROJECT_ID;
const scanResultTopic = process.env.SCAN_RESULT_TOPIC;
const deploymentName = process.env.DEPLOYMENT_NAME;
const reportObjectKey = process.env.REPORT_OBJECT_KEY === 'True';

const storage = new Storage();
const pubSubClient = new PubSub({ projectId: scannerProjectID });

let version;
try {
  const rawData = fs.readFileSync('package.json')
  version = JSON.parse(rawData).version;
} catch (error) {
  console.log('failed to get version.', error);
}

functions.http('handler', async (req, res) => {
  const body = req.body;
  const { file: { bucket, name, crc32c, etag } } = body;
  console.info(`Function version: ${version}`);
  console.info(`Trigger scan for file: ${name} in ${bucket}`);

  try {
    const url = await generateV4ReadSignedUrl(bucket, name).catch(console.error);

    const scanMessage = {
      signed_url: url,
      scan_result_topic: scanResultTopic,
      deployment_name: deploymentName,
      report_object_key: reportObjectKey,
      file_attributes: {
        etag,
        checksums: {
          crc32c
        }
      }
    };
    await publishMessage(JSON.stringify(scanMessage), scannerQueueTopic);
    res.send('OK');
  } catch (error) {
    console.error(error);
    res.status(500).send(error.message);
  }
});

async function generateV4ReadSignedUrl(bucketName, fileName) {
  try {
    // These options will allow temporary read access to the file
    const options = {
      version: 'v4',
      action: 'read',
      expires: Date.now() + 60 * 60 * 1000 // 1 hour
    };

    // Get a v4 signed URL for reading the file
    const [url] = await storage
      .bucket(bucketName)
      .file(fileName)
      .getSignedUrl(options);

    return url;
  } catch (error) {
    console.error('Failed to sign an url:', error);
    throw error;
  }
}

async function publishMessage(message, topic) {
  try {
    const messageId = await pubSubClient.topic(topic).publishMessage({ data: Buffer.from(message) })
    console.log(`Message ${messageId} published.`)
  } catch (error) {
    console.error('Received error while publishing scan message:', error)
    throw error
  }
}
