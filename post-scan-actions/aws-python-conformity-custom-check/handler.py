import boto3
import json
import os
import urllib3

# import datetime

http = urllib3.PoolManager()

region = os.environ.get("CC_REGION", "us-west-2")
ccsecretsarn = os.environ["CC_API_SECRETS_ARN"]
customcheckid = os.environ.get("CC_CUSTOMCHECKID", "CUSTOM-001").upper()
customchecksev = os.environ.get("CC_CHECKSEV", "VERY_HIGH").upper()

secrets = boto3.client("secretsmanager").get_secret_value(SecretId=ccsecretsarn)
secrets_data = json.loads(secrets["SecretString"])
apikey = secrets_data["ccapikey"]

headers = {
    "Content-Type": "application/vnd.api+json",
    "Authorization": "ApiKey " + apikey,
}


def get_cc_accountid(awsaccountid):
    accountsapi = f"https://{region}-api.cloudconformity.com/v1/accounts"
    r = http.request("GET", accountsapi, headers=headers)
    accounts = json.loads(r.data.decode("utf-8"))["data"]
    for account in accounts:
        try:
            if account["attributes"]["awsaccount-id"] == awsaccountid:
                return account["id"]
        except:
            pass


def lambda_handler(event, context):

    for record in event["Records"]:

        # Message details from SNS event
        message = json.loads(record["Sns"]["Message"])
        print(record["Sns"]["Message"])
        findings = message["scanning_result"].get("Findings")

        if findings:
            # Get AWS Account Info
            arn = json.dumps(record["EventSubscriptionArn"])
            aws_region = arn.split(":")[3].strip()
            account_id = arn.split(":")[4].strip()
            # Get Conformity Account ID for AWS Account
            ccaccountid = get_cc_accountid(account_id)

            # Get the bucket & object details
            bucketname = message["file_url"].split(".s3.amazonaws.com/")[0][8:]
            fileprefix = message["file_url"].split(".s3.amazonaws.com/")[1]
            filename = message["file_url"].split("/")[-1]
            s3uri = f"s3://{bucketname}/{fileprefix}"
            s3arn = f"arn:aws:s3:::{bucketname}/{fileprefix}"
            s3consoleurl = f"https://s3.console.aws.amazon.com/s3/buckets/{bucketname}?region={aws_region}&prefix={fileprefix}"

            # Generate TTL to expire message (not currently supported by conformity custom checks api - coming soon?)
            # timenow = datetime.datetime.now()
            # ttl = timenow + datetime.timedelta(days=1)
            # ttlepoch = round(datetime.datetime.timestamp(ttl))

            malwares = []
            types = []
            for finding in message["scanning_result"]["Findings"]:
                malwares.append(finding.get("malware"))
                types.append(finding.get("type"))

                checksdata = {
                    "data": [
                        {
                            "type": "checks",
                            "attributes": {
                                "rule-title": "C1 File Storage Security - Malware Detected",
                                "message": f"Object {filename} in bucket {bucketname} contains malware",
                                "not-scored": False,
                                "region": aws_region,
                                "resource": s3uri.replace("/", ":"),
                                "risk-level": customchecksev,
                                "status": "FAILURE",
                                "service": "S3",
                                "categories": ["security"],
                                "link": s3consoleurl,
                                # "ttl": ttlepoch,
                                "extradata": [
                                    {
                                        "label": "Malware Name",
                                        "name": "Malware Name",
                                        "type": "Meta",
                                        "value": ", ".join(malwares),
                                    },
                                    {
                                        "label": "Malware Type",
                                        "name": "Malware Type",
                                        "type": "Meta",
                                        "value": ", ".join(types),
                                    },
                                    {
                                        "label": "S3 URI",
                                        "name": "S3 URI",
                                        "type": "Meta",
                                        "value": s3uri,
                                    },
                                    {
                                        "label": "S3 ARN",
                                        "name": "S3 ARN",
                                        "type": "Meta",
                                        "value": s3arn,
                                    },
                                    {
                                        "label": "S3 Console URL",
                                        "name": "S3 Console URL",
                                        "type": "Meta",
                                        "value": s3consoleurl,
                                    },
                                ],
                            },
                            "relationships": {
                                "account": {
                                    "data": {"id": ccaccountid, "type": "accounts"}
                                },
                                "rule": {
                                    "data": {"id": customcheckid, "type": "rules"}
                                },
                            },
                        }
                    ]
                }

                bodyencoded = json.dumps(checksdata).encode("utf-8")
                checksapi = f"https://{region}-api.cloudconformity.com/v1/checks"

                r = http.request("POST", checksapi, body=bodyencoded, headers=headers)
                print(r.data.decode("utf-8"))
