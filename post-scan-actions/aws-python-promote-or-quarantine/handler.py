import os
import re
import json
import time
import urllib.parse

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from botocore.exceptions import ClientError

VALID_ACL = {
    'private',
    'public-read',
    'public-read-write',
    'authenticated-read',
    'aws-exec-read',
    'bucket-owner-read',
    'bucket-owner-full-control',
}

VALID_METADATA = [
    'CacheControl',
    'ContentDisposition',
    'ContentEncoding',
    'ContentLanguage',
    'ContentType',
    'Metadata',
    'WebsiteRedirectLocation',
    'Expires'
]

MODES = {
    'move',
    'copy',
}

DEFAULT_MODE = 'move'
S3_DOMAIN_PATTERN = 's3(\..+)?\.amazonaws.com'
FSS_TAG_PREFIX = 'fss-'

CODE_EMPTY = 0
CODE_SKIP_MULTIPLE = 100
CODE_MISC = 199

CODE_MESSAGES = {
    CODE_EMPTY: '',
    CODE_SKIP_MULTIPLE : 'incomplete scan due to multiple reasons',
    101: 'incomplete archive file extraction due to file too large',
    102: 'incomplete archive file extraction due to too many files in archive',
    103: 'incomplete archive file extraction due to too many archive layers',
    104: 'incomplete archive file extraction due to compression ratio exceeds limit',
    105: 'incomplete archive file extraction due to unsupported compression method',
    106: 'incomplete archive file extraction due to corrupted compression file',
    107: 'incomplete archive file extraction due to archive file encryption',
    108: 'incomplete scan due to Microsoft Office file encryption',
    CODE_MISC: 'incomplete scan due to miscellaneous reason. Provide the fss-scan-detail-code tag value to Trend Micro support',
}

S3_MAX_CONCURRENCY = 940
S3_MULTIPART_CHUNK_SIZE = 16 * 1024 * 1024   # 16MB
S3_MAX_POOL_CONNECTIONS = 940
S3_MAX_ATTEMPTS = 100

transfer_config = TransferConfig(max_concurrency=S3_MAX_CONCURRENCY, multipart_chunksize=S3_MULTIPART_CHUNK_SIZE)
config = Config(max_pool_connections=S3_MAX_POOL_CONNECTIONS, retries = {'max_attempts': S3_MAX_ATTEMPTS})
s3 = boto3.client('s3', config=config)

def get_mode_from_env(mode_key):
    mode = os.environ.get(mode_key, 'move').lower()
    return mode if mode in MODES else DEFAULT_MODE

def get_promote_mode():
    return get_mode_from_env('PROMOTEMODE')

def get_quarantine_mode():
    return get_mode_from_env('QUARANTINEMODE')

def parse_s3_object_url(url_string):
    url = urllib.parse.urlparse(url_string)
    # check pre-signed URL type, path or virtual
    if re.fullmatch(S3_DOMAIN_PATTERN, url.netloc):
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
            if not tag['Key'].startswith(FSS_TAG_PREFIX)
        )
    except ClientError as ex:
        print('failed to get existing tags: ' + str(ex))
        return None

def get_metadata(bucket_name, object_key):
    try:
        metadata = s3.head_object(Bucket=bucket_name, Key=object_key)
        return dict(filter(lambda elem: elem[0] in VALID_METADATA, metadata.items()))
    except ClientError as ex:
        print('failed to get existing metadata: ' + str(ex))
        return None

def copy_object(source_bucket, source_key, dest_bucket, dest_key, tags, metadata, acl=None):
    params = {
        'TaggingDirective': 'REPLACE',
        'Tagging': '&'.join(tags),
        **(metadata if metadata else {})
    }

    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }

    if acl and acl in VALID_ACL:
        params['ACL'] = acl

    s3.copy(copy_source, dest_bucket, dest_key, params, Config=transfer_config)

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

        scanning_result = message['scanning_result']
        findings = scanning_result.get('Findings')

        operation = 'quarantine' if findings else 'promotion'
        mode = quarantine_mode if findings else promote_mode
        dst_bucket = quarantine_bucket if findings else promote_bucket
        scan_result = 'malicious' if findings else 'no issues found'
        scan_date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(message['timestamp']))

        if not dst_bucket:
            print(f'Skip: No bucket specified for {operation}')
            continue

        codes = scanning_result['Codes']
        code = CODE_EMPTY
        if len(codes) > 0:
            code = CODE_SKIP_MULTIPLE if len(codes) > 1 else codes[0]
        tags = [
            f'{FSS_TAG_PREFIX}scanned=true',
            f'{FSS_TAG_PREFIX}scan-date={urllib.parse.quote_plus(scan_date)}',
            f'{FSS_TAG_PREFIX}scan-result={urllib.parse.quote_plus(scan_result)}',
            f'{FSS_TAG_PREFIX}scan-detail-code={str(code)}',
            f'{FSS_TAG_PREFIX}scan-detail-message={urllib.parse.quote_plus(CODE_MESSAGES.get(code, CODE_MESSAGES[CODE_MISC]))}',
        ]
        existing_tag_set = get_existing_tag_set(src_bucket, object_key)
        if existing_tag_set:
            tags.extend(existing_tag_set)

        metadata = get_metadata(src_bucket, object_key)

        copy_object(
            source_bucket=src_bucket,
            dest_bucket=dst_bucket,
            source_key=object_key,
            dest_key=object_key,
            tags=tags,
            metadata=metadata,
            acl=acl,
        )

        if mode == 'move':
            delete_objects(bucket=src_bucket, prefix='', objects=[object_key])

        print(f'File {operation} successful (mode: {mode})')
