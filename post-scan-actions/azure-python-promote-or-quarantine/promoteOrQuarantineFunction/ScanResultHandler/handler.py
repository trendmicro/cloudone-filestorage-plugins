import logging
import os
import json
import time
import urllib.parse

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient, BlobServiceClient
from azure.storage.blob._shared.models import AccountSasPermissions
from azure.storage.blob._shared_access_signature import BlobSharedAccessSignature
from datetime import datetime, timedelta

# Hide verbose HTTP logging
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)

MODES = {
    'move',
    'copy',
}
DEFAULT_MODE = 'move'

FSS_TAG_PREFIX = 'fss-'
FSS_METADATA_PREFIX = 'fss'

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

def main(message: func.ServiceBusMessage):
    # Log the Service Bus Message as plaintext

    message_body = message.get_body().decode("utf-8")

    logging.info('Python ServiceBus topic trigger processed message.')
    logging.info(f'Message Body: {message_body}')

    quarantine_storage_connection_string = os.environ.get('QUARANTINE_STORAGE_CONNECTION_STRING')
    promote_storage_connection_string = os.environ.get('PROMOTE_STORAGE_CONNECTION_STRING')

    promote_mode = get_promote_mode()
    quarantine_mode = get_quarantine_mode()

    message = json.loads(message_body)
    file_url = message['file_url']
    (_, blob_container, blob_name) = parse_blob_information(file_url)

    credential = DefaultAzureCredential(exclude_environment_credential=True)
    source_blob_service_client = BlobServiceClient(
        account_url=get_blob_account_url(file_url),
        credential=credential
    )
    blob_url_sas = get_blob_url_sas(source_blob_service_client, file_url)

    protecting_blob_client = source_blob_service_client.get_blob_client(blob_container, blob_name)
    existing_metadata = get_existing_metadata(protecting_blob_client)
    existing_tags = get_existing_tags(protecting_blob_client)

    result = message['scanning_result']
    findings = result['Findings']
    logging.info(f'findings: {json.dumps(findings)}')

    operation = 'quarantine' if findings else 'promotion'
    mode = quarantine_mode if findings else promote_mode
    dest_storage_connection_string = quarantine_storage_connection_string if findings else promote_storage_connection_string
    scan_result = 'malicious' if findings else 'no issues found'
    scan_date = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(message['timestamp']))

    if not dest_storage_connection_string:
        print(f'Skip: No storage connection string specified for {operation}')
        return

    codes = result['Codes']
    code = CODE_EMPTY
    if len(codes) > 0:
        code = CODE_SKIP_MULTIPLE if len(codes) > 1 else codes[0]
    fssTags = {
        'scanned': 'true',
        'scanDate': scan_date,
        'scanResult': scan_result,
        'scanDetailCode': str(code),
        'scanDetailMessage': CODE_MESSAGES.get(code, CODE_MESSAGES[CODE_MISC])
    }
    logging.info(f'FSS tags: {fssTags}')
    metadata = compose_metadata(existing_metadata, fssTags)
    tags = compose_tags(existing_tags, fssTags)

    dest_blob_service_client = BlobServiceClient.from_connection_string(dest_storage_connection_string)
    copy_object(
        source_blob_url=blob_url_sas,
        container=blob_container,
        blob_name=blob_name,
        metadata=metadata,
        tags=tags,
        dest_blob_service_client=dest_blob_service_client,
    )

    if mode == 'move':
        protecting_blob_client.delete_blob()

    logging.info(f'File {operation} is successful (mode: {mode})')


def copy_object(source_blob_url, container, blob_name, metadata, tags, dest_blob_service_client: BlobServiceClient):
    container_client = dest_blob_service_client.get_container_client(container)
    if not container_client.exists():
        container_client.create_container()

    blob_client = container_client.get_blob_client(blob_name)
    copy_status = blob_client.start_copy_from_url(
        source_url=source_blob_url,
        metadata=metadata,
        tags=tags,
        requires_sync=True
    )
    logging.info(f'copy status: {copy_status}')

def compose_tags(existing_tags, fssTags):
    return {
        **existing_tags,
        **{
            f'{FSS_TAG_PREFIX}scanned': fssTags['scanned'],
            f'{FSS_TAG_PREFIX}scan-date': fssTags['scanDate'],
            f'{FSS_TAG_PREFIX}scan-result': fssTags['scanResult'],
            f'{FSS_TAG_PREFIX}scan-detail-code': fssTags['scanDetailCode'],
            f'{FSS_TAG_PREFIX}scan-detail-message': fssTags['scanDetailMessage'],
        }
    }

def compose_metadata(existing_metadata, fssTags):
    return {
        **existing_metadata,
        **{
            f'{FSS_METADATA_PREFIX}Scanned': fssTags['scanned'],
            f'{FSS_METADATA_PREFIX}ScanDate': fssTags['scanDate'],
            f'{FSS_METADATA_PREFIX}ScanResult': fssTags['scanResult'],
            f'{FSS_METADATA_PREFIX}ScanDetailCode': fssTags['scanDetailCode'],
            f'{FSS_METADATA_PREFIX}ScanDetailMessage': fssTags['scanDetailMessage'],
        }
    }

def get_mode_from_env(mode_key):
    mode = os.environ.get(mode_key, 'move').lower()
    return mode if mode in MODES else DEFAULT_MODE

def get_promote_mode():
    return get_mode_from_env('PROMOTEMODE')

def get_quarantine_mode():
    return get_mode_from_env('QUARANTINEMODE')

def get_blob_account_url(file_url):
    return '/'.join(file_url.split('/')[0:3])

def compose_blob_url(file_url):
    split_url = file_url.split('/')
    blob_url = '/'.join([
        get_blob_account_url(file_url),
        split_url[3],
        *list(map(lambda e: urllib.parse.quote(e), split_url[4:]))
    ])
    return blob_url

def parse_blob_information(file_url):
    split_url = file_url.split('/')
    blob_account_name = split_url[2].split('.')[0]
    blob_container = split_url[3]
    blob_name = '/'.join(split_url[4:])
    return blob_account_name, blob_container, blob_name

def get_blob_url_sas(blob_service_client, file_url):
    try:
        (blob_account_name, blob_container, blob_name) = parse_blob_information(file_url)
        logging.info(f'source blob: {blob_account_name}/{blob_container}/{blob_name}')

        delegation_key = blob_service_client.get_user_delegation_key(key_start_time=datetime.utcnow(), key_expiry_time=datetime.utcnow() + timedelta(hours=1))
        blob_sas = BlobSharedAccessSignature(account_name=blob_account_name, user_delegation_key=delegation_key)
        sas_token = blob_sas.generate_blob(container_name=blob_container, blob_name=blob_name, permission=AccountSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1))
        return f'{compose_blob_url(file_url)}?{sas_token}'
    except Exception as ex:
        logging.error('failed to get SAS for blob: ' + str(ex))
        raise

def exclude_key_prefix(d, key_prefix):
    if d is None:
        return {}
    return dict(filter(lambda elem: not elem[0].startswith(key_prefix), d.items()))

def get_existing_metadata(blob_client: BlobClient):
    try:
        return exclude_key_prefix(blob_client.get_blob_properties().metadata, FSS_METADATA_PREFIX)
    except Exception as ex:
        logging.warn(f'failed to get existing metadata: {ex}')
    return {}

def get_existing_tags(blob_client: BlobClient):
    try:
        return exclude_key_prefix(blob_client.get_blob_tags(), FSS_TAG_PREFIX)
    except Exception as ex:
        logging.warn(f'failed to get existing tags: {ex}')
    return {}
