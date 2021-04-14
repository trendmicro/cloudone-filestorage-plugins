import os
import re
import json
import time
import urllib.parse

import boto3

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

def copy_object(source_bucket, source_key, dest_bucket, dest_key, acl=None):
    s3 = boto3.client('s3')

    params = {
        'Bucket': dest_bucket,
        'CopySource': {'Bucket': source_bucket, 'Key': source_key},
        'Key': dest_key,
    }

    if acl and acl in valid_acl:
        params['ACL'] = acl

    s3.copy_object(**params)

def delete_objects(bucket, prefix, objects):
    s3 = boto3.client('s3')
    objects = {'Objects': [{'Key': prefix + o} for o in objects]}
    s3.delete_objects(Bucket=bucket, Delete=objects)

def lambda_handler(event, context):
    acl = os.environ.get('ACL')

    quarantine_bucket = os.environ.get('QUARANTINEBUCKET')
    promote_bucket = os.environ.get('PROMOTEBUCKET')

    promote_mode = get_promote_mode()
    quarantine_mode = get_quarantine_mode()

    time.sleep(15)
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

        if not dst_bucket:
            print(f'Skip: No bucket specified for {operation}')
            continue

        copy_object(
            source_bucket=src_bucket,
            dest_bucket=dst_bucket,
            source_key=object_key,
            dest_key=object_key,
            acl=acl,
        )

        if mode == 'move':
            delete_objects(bucket=src_bucket, prefix='', objects=[object_key])

        print(f'File {operation} successful (mode: {mode})')
