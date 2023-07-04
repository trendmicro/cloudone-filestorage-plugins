import base64
import json
import logging
import os
import time
import urllib.parse

from google.cloud import storage

MODES = {
    'move',
    'copy',
}
DEFAULT_MODE = 'move'

FSS_TAG_PREFIX = 'fss-'

CODE_EMPTY = 0
CODE_SKIP_MULTIPLE = 100
CODE_MISC = 199

CODE_MESSAGES = {
    CODE_EMPTY: '',
    CODE_SKIP_MULTIPLE: 'incomplete scan due to multiple reasons',
    101: 'incomplete archive file extraction due to file too large',
    102: 'incomplete archive file extraction due to too many files in archive',
    103: 'incomplete archive file extraction due to too many archive layers',
    104: 'incomplete archive file extraction due to compression ratio exceeds limit',
    105: 'incomplete archive file extraction due to unsupported compression method',
    106: 'incomplete archive file extraction due to corrupted compression file',
    107: 'incomplete archive file extraction due to archive file encryption',
    108: 'incomplete scan due to Microsoft Office file encryption',
    109: 'incomplete scan due to PDF encryption',
    CODE_MISC: 'incomplete scan due to miscellaneous reason. Provide the fss-scan-detail-code tag value to Trend Micro support',
}

def parse_object_url(input_url):
    url = urllib.parse.urlparse(input_url)
    paths = url.path.split('/', 2)
    return paths[1], urllib.parse.unquote(paths[2])

def main(event, context):
    print(f'Context: {context}')

    base64_data = event.get('data', '')
    base64_bytes = base64_data.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = json.loads(message_bytes.decode('ascii'))
    print(f'Message: {message}')

    bucket_name, object_name = parse_object_url(message['file_url'])

    quarantine_storage_bucket = os.environ.get('QUARANTINE_STORAGE_BUCKET')
    promote_storage_bucket = os.environ.get('PROMOTE_STORAGE_BUCKET')

    promote_mode = get_promote_mode()
    quarantine_mode = get_quarantine_mode()

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    _object = bucket.get_blob(object_name)

    result = message['scanning_result']
    findings = result['Findings']
    print(f'Findings: {findings}')

    scan_date = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(message['timestamp']))
    scan_result = 'malicious' if findings else 'no issues found'

    operation = 'quarantine' if findings else 'promotion'
    mode = quarantine_mode if findings else promote_mode
    dst_bucket_name = quarantine_storage_bucket if findings else promote_storage_bucket

    if not dst_bucket_name:
        print(f'Skip: No storage connection string specified for {operation}')
        return

    codes = result['Codes']
    code = CODE_EMPTY
    if len(codes) > 0:
        code = CODE_SKIP_MULTIPLE if len(codes) > 1 else codes[0]
    fss_metadata = {
        f'{FSS_TAG_PREFIX}scanned' : 'true',
        f'{FSS_TAG_PREFIX}scan-date' : scan_date,
        f'{FSS_TAG_PREFIX}scan-result' : scan_result,
        f'{FSS_TAG_PREFIX}scan-detail-code' : str(code),
        f'{FSS_TAG_PREFIX}scan-detail-message' : CODE_MESSAGES.get(code, CODE_MESSAGES[CODE_MISC]),
    }
    print(f'FSS metadata: {fss_metadata}')
    set_object_metadata(_object, fss_metadata)
    copy_object(storage_client, bucket_name, dst_bucket_name, _object)

    if mode == 'move':
        bucket = storage_client.bucket(bucket_name)
        bucket.delete_blob(object_name)

    print(f'File {operation} is successful (mode: {mode})')

def set_object_metadata(_object, metadata):
    """Set metadata for object."""
    try:
        _object.metadata = metadata
        _object.patch()
        print(f'Metadata: {metadata} set for {_object.name}')
    except Exception as ex:
        print('failed to set object metadata: ' + str(ex))

def copy_object(storage_client: storage.Client, source_bucket_name: str, destination_bucket_name: str, _object):
    try:
        source_bucket = storage_client.bucket(source_bucket_name)
        destination_bucket = storage_client.bucket(destination_bucket_name)
        new_object = source_bucket.copy_blob(_object, destination_bucket)
        print(f'Copied {_object.name} to {destination_bucket_name} as {new_object.name}')
    except Exception as e:
        logging.error(e)

def get_mode_from_env(mode_key):
    mode = os.environ.get(mode_key, 'move').lower()
    return mode if mode in MODES else DEFAULT_MODE

def get_promote_mode():
    return get_mode_from_env('PROMOTE_MODE')

def get_quarantine_mode():
    return get_mode_from_env('QUARANTINE_MODE')

def exclude_key_prefix(d, key_prefix):
    if d is None:
        return {}
    return dict(filter(lambda elem: not elem[0].startswith(key_prefix), d.items()))
