import json
import os
import boto3
import time
from botocore.exceptions import ClientError
import urllib.parse
import re

s3_domain_pattern = 's3(\..+)?\.amazonaws.com'

def parse_s3_object_url(url_string):
    url = urllib.parse.urlparse(url_string)
    # check pre-signed URL type, path or virtual
    if re.fullmatch(s3_domain_pattern, url.netloc):
        bucket = url.path.split('/')[1]
        s3_object = '/'.join(url.path.split('/')[2:])
    else:
        bucket = url.netloc.split('.')[0]
        s3_object = url.path[1:]
    object_key = urllib.parse.unquote_plus(s3_object)

    return bucket, object_key

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
    quarantine_bucket = os.environ['QUARANTINEBUCKET']
    promote_bucket = os.environ['PROMOTEBUCKET']
    time.sleep(15)
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        print(json.dumps(message))

        src_bucket, object_key = parse_s3_object_url(message['file_url'])
        print('Source Bucket: ', src_bucket)
        print('Object Key: ', object_key)

        findings = message['scanning_result'].get('Findings')

        if not findings:
            copy_object(source_bucket=src_bucket, dest_bucket=promote_bucket, source_key=object_key, dest_key=object_key)
            delete_objects(bucket=src_bucket, prefix='', objects=[object_key])
            print('Promoted file successfully')
        else:
            copy_object(source_bucket=src_bucket, dest_bucket=quarantine_bucket, source_key=object_key, dest_key=object_key)
            delete_objects(bucket=src_bucket, prefix='', objects=[object_key])
            print('Quarantined file successfully')
