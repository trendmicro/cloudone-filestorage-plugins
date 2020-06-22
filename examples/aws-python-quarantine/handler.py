import json
import os
import logging
import boto3
from botocore.exceptions import ClientError
import urllib.parse
import time

def copy_object(source_bucket, source_key, dest_bucket,dest_key ):
    s3 = boto3.client('s3')
    s3.copy_object(
        Bucket=dest_bucket, 
        CopySource={'Bucket': source_bucket, 'Key':source_key},
        Key=dest_key
    )

def delete_objects(bucket, prefix, objects):
    s3 = boto3.client('s3')
    objects = {'Objects': [{'Key': prefix + o} for o in objects]}
    s3.delete_objects(Bucket=bucket, Delete=objects)

def lambda_handler(event, context):
    quarantineBucket = os.environ['QUARANTINEBUCKET']
    promoteBucket = os.environ['PROMOTEBUCKET']
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        scanResults = message['scanning_result']
        findings = scanResults.get('Findings')
        URL = message["file_url"]
        result = message["scanner_status_message"]
        if result == "unsuccessful scan":
            return False
        if result != "successful scan":
            return {'statusCode': 200}
        split = URL.split("/")
        bucket = split[2]
        S3object = split[-1]
        ObjectKey = urllib.parse.unquote_plus(S3object)
        srcBucket = urllib.parse.unquote_plus(bucket).split('.')[0]

        if not findings:
            copy_object(source_bucket=srcBucket, dest_bucket=promoteBucket, source_key=ObjectKey, dest_key=ObjectKey)
            delete_objects(bucket=srcBucket, prefix='', objects=[ObjectKey])
        else:
            copy_object(source_bucket=srcBucket, dest_bucket=quarantineBucket, source_key=ObjectKey, dest_key=ObjectKey)
            delete_objects(bucket=srcBucket, prefix='', objects=[ObjectKey])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }