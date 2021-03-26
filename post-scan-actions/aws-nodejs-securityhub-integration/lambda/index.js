const AWS = require('aws-sdk');
const uuid = require('uuid');

const parseDetectionPath = (path) => {
  const bucket = path.substring(8, path.indexOf('.s3.'));
  const key = path.split('/').slice(3).join('/');
  return {
    bucket,
    key
  };
};

const publishToSecurityHub = async (securityhub, securityHubArn, accountId, malwareName, bucket, key ) => {
  const date = new Date().toISOString();
  const params = {
    Findings : [
      {
        AwsAccountId: accountId,
        CreatedAt: date,
        Description: "Malware found!",
        GeneratorId: "FSS",
        Id: `${accountId}/${uuid.v4()}`,
        ProductArn: securityHubArn,
        SchemaVersion: "2018-10-08",
        Resources: [
          {
            Id: key,
            Type: "AwsS3Object"
          },
          {
            Id: bucket,
            Type: "AwsS3Bucket"
          },
        ],
        Malware: [ 
          { 
              Name: malwareName,
              Path: key,
              State: "OBSERVED",
              Type: "POTENTIALLY_UNWANTED"
          }
      ],
        Severity: {
          Label: "HIGH"
        },
        Title: "S3 Object had malware detected by FSS.",
        Types: [
          "Unusual Behaviors/Data"
        ],
        UpdatedAt: date
      }
    ]
  };
  try {
    const result = await securityhub.batchImportFindings(params).promise();
    console.log(result);
    return result;
  } catch (error) {
    console.error(error);
    return error;
  }
};

exports.handler = async (event) => {
  const securityHubArn = process.env.SECURITY_HUB_ARN;
  const accountId = process.env.ACCOUNT_ID;
  const securityhub = new AWS.SecurityHub();
  return Promise.all(event.Records.map(async (record) => {
    console.log(record);
    const message = JSON.parse(record.Sns.Message);
    const findings = message.scanning_result.Findings;
    
    const results = [];
    
    if (findings) {
      findings.forEach(finding => {
        const malwareName = finding.malware;
        const path = parseDetectionPath(message.file_url);
        console.log(path);
        const findingResult = publishToSecurityHub(securityhub, securityHubArn, accountId, malwareName, path.bucket, path.key);
        results.push(findingResult);
        console.log('findingResult: ', findingResult);
      });
    }
    console.log(results);
    if (results){
      await Promise.all(results);
    }
  }));
};
