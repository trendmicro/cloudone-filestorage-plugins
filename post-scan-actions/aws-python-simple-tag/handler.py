import json
import boto3
from botocore.exceptions import ClientError
import urllib.parse
import time
import re

s3_client = boto3.client('s3')
fss_tag_prefix = ''

def get_existing_tag_set(bucket_name, object_name):
    try:
        response = s3_client.get_object_tagging(Bucket=bucket_name, Key=object_name)
        return list(map(lambda tag: [tag['Key'], tag['Value']], response['TagSet']))
    except ClientError as ex:
        print('failed to get existing tags: ' + str(ex))
        return None

def tag_object(bucket_name, object_name, tag):
    existing_tag_list = get_existing_tag_set(bucket_name, object_name)
    if existing_tag_list:
        for k, v in existing_tag_list:
            #if k is in tag list, then skip this k
            if list(filter(lambda tag: tag['Key']==k, tag['TagSet'])):
                continue
            #append existing tag
            tag['TagSet'].append({'Key': k,
                 'Value': v if v is not None else ''})
    try:
        s3_client.put_object_tagging(
            Bucket=bucket_name, Key=object_name, Tagging=tag)
        print('the object has been tagged with scanning results')
    except ClientError as e:
        print('failed to tag object: ' + str(e))

def make_tags(tags):
    tag_list = []
    for k, v in tags.items():
        tag_list.append({'Key': k,
                         'Value': v if v is not None else ''})
    return {'TagSet': tag_list}

def get_function_version():
    """Get function's version."""
    try:
        with open('version.json') as version_file:
            version = json.load(version_file)
            return version['version']
    except Exception as ex:
        print('failed to get version: ' + str(ex))
        return ''

def lambda_handler(event, context):

    version = get_function_version()
    print(f'version: {version}')

    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        print(json.dumps(message))

        s3_domain_pattern = 's3(\..+)?\.amazonaws.com'

        url = urllib.parse.urlparse(message['file_url'])
        # check pre-signed URL type, path or virtual
        if re.fullmatch(s3_domain_pattern, url.netloc):
            bucket = url.path.split('/')[1]
            s3_object = '/'.join(url.path.split('/')[2:])
        else:
            bucket = url.netloc.split('.')[0]
            s3_object = url.path[1:]

        object_key = urllib.parse.unquote_plus(s3_object)

        status = message['scanner_status']
        if status != 0:
            tag_object(bucket, object_key, make_tags({
                f'{fss_tag_prefix}scanned': 'false',
                f'{fss_tag_prefix}scan-result': 'failure',
                f'{fss_tag_prefix}scan-date': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(message['timestamp'])),
                f'{fss_tag_prefix}error-message': message['scanner_status_message'],
            }))
            continue

        result = message['scanning_result']
        findings = result['Findings']
        print('findings: ' + json.dumps(findings))
        scan_result = 'no issue found'
        if len(findings) > 0:
            scan_result = 'malicious'
        print('scan result: ' + scan_result)

        tag_object(bucket, object_key, make_tags({
            f'{fss_tag_prefix}scanned': 'true',
            f'{fss_tag_prefix}scan-date': time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(message['timestamp'])),
            f'{fss_tag_prefix}scan-result': scan_result,
        }))