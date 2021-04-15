import os
import re
import json
import time
import urllib.parse

import boto3
from botocore.exceptions import ClientError

valid_acl = {
    'private',
    'public-read',
    'public-read-write',
    'authenticated-read',
    'aws-exec-read',
    'bucket-owner-read',
    'bucket-owner-full-control',
}

modes = {
    'move',
    'copy',
}

default_mode = 'move'
s3_domain_pattern = 's3(\..+)?\.amazonaws.com'
fss_tag_prefix = 'fss-'

s3 = boto3.client('s3')

def get_mode_from_env(mode_key):
    mode = os.environ.get(mode_key, 'move').lower()
    return mode if mode in modes else default_mode

def get_promote_mode():
    return get_mode_from_env('PROMOTEMODE')

def get_quarantine_mode():
    return get_mode_from_env('QUARANTINEMODE')

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

def get_existing_tag_set(bucket_name, object_key):
    try:
        response = s3.get_object_tagging(Bucket=bucket_name, Key=object_key)
        return list(
            f'{urllib.parse.quote_plus(tag["Key"])}={urllib.parse.quote_plus(tag["Value"])}'
            for tag in response['TagSet']
            if not tag['Key'].startswith(fss_tag_prefix)
        )
    except ClientError as ex:
        print('failed to get existing tags: ' + str(ex))
        return None

def copy_object(source_bucket, source_key, dest_bucket, dest_key, tags, acl=None):
    params = {
        'Bucket': dest_bucket,
        'CopySource': {'Bucket': source_bucket, 'Key': source_key},
        'Key': dest_key,
        'TaggingDirective': 'REPLACE',
        'Tagging': '&'.join(tags),
    }

    if acl and acl in valid_acl:
        params['ACL'] = acl

    s3.copy_object(**params)

def delete_objects(bucket, prefix, objects):
    objects = {'Objects': [{'Key': prefix + o} for o in objects]}
    s3.delete_objects(Bucket=bucket, Delete=objects)

def lambda_handler(event, context):
    acl = os.environ.get('ACL')

    quarantine_bucket = os.environ.get('QUARANTINEBUCKET')
    promote_bucket = os.environ.get('PROMOTEBUCKET')

    promote_mode = get_promote_mode()
    quarantine_mode = get_quarantine_mode()

    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        print(json.dumps(message))

        if message['scanner_status'] != 0:
            print('Skip: ', message['scanner_status_message'])
            continue

        src_bucket, object_key = parse_s3_object_url(message['file_url'])
        print('Source Bucket: ', src_bucket)
        print('Object Key: ', object_key)

        findings = message['scanning_result'].get('Findings')

        operation = 'quarantine' if findings else 'promotion'
        mode = quarantine_mode if findings else promote_mode
        dst_bucket = quarantine_bucket if findings else promote_bucket
        scan_result = 'malicious' if findings else 'no issues found'
        scan_date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(message['timestamp']))

        if not dst_bucket:
            print(f'Skip: No bucket specified for {operation}')
            continue

        tags = [
            f'{fss_tag_prefix}scanned=true',
            f'{fss_tag_prefix}scan-date={urllib.parse.quote_plus(scan_date)}',
            f'{fss_tag_prefix}scan-result={urllib.parse.quote_plus(scan_result)}',
        ]
        existing_tag_set = get_existing_tag_set(src_bucket, object_key)
        if existing_tag_set:
            tags.extend(existing_tag_set)

        copy_object(
            source_bucket=src_bucket,
            dest_bucket=dst_bucket,
            source_key=object_key,
            dest_key=object_key,
            tags=tags,
            acl=acl,
        )

        if mode == 'move':
            delete_objects(bucket=src_bucket, prefix='', objects=[object_key])

        print(f'File {operation} successful (mode: {mode})')
