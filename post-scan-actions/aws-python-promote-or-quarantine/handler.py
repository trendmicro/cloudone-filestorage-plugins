import os
import re
import json
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Any, List

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
    CODE_SKIP_MULTIPLE: 'incomplete scan due to multiple reasons',
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
S3_MULTIPART_CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
S3_MAX_POOL_CONNECTIONS = 940
S3_MAX_ATTEMPTS = 100

transfer_config = TransferConfig(max_concurrency=S3_MAX_CONCURRENCY, multipart_chunksize=S3_MULTIPART_CHUNK_SIZE)
config = Config(max_pool_connections=S3_MAX_POOL_CONNECTIONS, retries={'max_attempts': S3_MAX_ATTEMPTS})
s3_client = boto3.client('s3', config=config)


def get_mode_from_env(mode_key: str) -> str:
    """
    A small function that will take in a ENV var key and return a value.

    If the key provided does not match the expected keys, it will default to 'move'

    :param mode_key: (required) A string key that maps to an ENV var ('move' or 'copy')
    :return: A string value of the ENV var ('move' or 'copy')
    """
    mode = os.getenv(mode_key, 'move').lower()
    return mode if mode in MODES else DEFAULT_MODE


@dataclass
class ObjectData:
    """Data-oriented class with attrs parsed from event data."""
    message: Dict[str, Any]

    scanner_status: str = field(init=False, repr=False)
    scanner_status_message: str = field(init=False, repr=False)
    file_url: str = field(init=False, repr=False)
    scanning_result: Dict[str, Any] = field(init=False, repr=False)
    findings: str = field(init=False, repr=False)
    timestamp: float = field(init=False, repr=False)
    codes: List[int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Runs after the required params are passed to class instance."""
        self.scanner_status = self.message.get('scanner_status')
        self.scanner_status_message = self.message.get('scanner_status_message')
        self.file_url = self.message.get('file_url')
        self.scanning_result = self.message.get('scanning_result')
        self.findings = self.scanning_result.get('Findings')
        self.timestamp = self.message.get('timestamp')
        self.codes = self.scanning_result.get('Codes')


class AssignTag:
    """Action-oriented class with attrs/methods for tagging S3 object."""

    def __init__(self, obj_data: ObjectData) -> None:
        self.obj_data = obj_data

        self.src_bucket: str = ''
        self.object_key: str = ''
        self.tag_list: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def _parse_s3_object_url(self) -> None:
        """
        Private method that will parse the pre-signed URL for S3 object.

        The pre-signed URL can either be a 'path' or 'virtual' type.
        Path Style Example: "https://s3.region-code.amazonaws.com/bucket-name/key-name"
        Virtual Style Example: "https://bucket-name.s3.region-code.amazonaws/key-name"

        :return: None
        """
        url = urllib.parse.urlparse(self.obj_data.file_url)
        # check pre-signed URL type, path or virtual
        if re.fullmatch(S3_DOMAIN_PATTERN, url.netloc):
            self.src_bucket = url.path.split('/')[1]
            s3_object = '/'.join(url.path.split('/')[2:])
        else:
            self.src_bucket = url.netloc.split('.')[0]
            s3_object = url.path[1:]
        self.object_key = urllib.parse.unquote_plus(s3_object)

    def _create_tags(self) -> None:
        """
        Private method to create base tag set to be applied to S3 object.

        The code that is assigned is based on the CODE_MESSAGES dict.

        :return: None
        """
        scan_date = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(self.obj_data.timestamp))
        scan_result = 'malicious' if self.obj_data.findings else 'no issues found'
        code = CODE_EMPTY
        if self.obj_data.codes:
            code = CODE_SKIP_MULTIPLE if len(self.obj_data.codes) > 1 else self.obj_data.codes[0]
        self.tag_list = [
            f'{FSS_TAG_PREFIX}scanned=true',
            f'{FSS_TAG_PREFIX}scan-date={scan_date}',
            f'{FSS_TAG_PREFIX}scan-result={scan_result}',
            f'{FSS_TAG_PREFIX}scan-detail-code={str(code)}',
            f'{FSS_TAG_PREFIX}scan-detail-message={CODE_MESSAGES.get(code, CODE_MESSAGES[CODE_MISC])}',
        ]

    def _get_metadata(self) -> None:
        """
        Private method that will call AWS API to return metadata from an S3 object without returning the object.

        Uses an anonymous function/higher-order ops to parse the object response from AWS API.

        :return: None
        """
        try:
            metadata = s3_client.head_object(Bucket=self.src_bucket, Key=self.object_key)
        except ClientError as err:
            print(f'failed to get existing metadata: {str(err)}')
        else:
            self.metadata = dict(filter(lambda elem: elem[0] in VALID_METADATA, metadata.items()))

    def _get_existing_tag_set(self) -> List[str]:
        """
        Private method that calls AWS API and checks for existing tags on S3 object.

        Uses Python list comprehension to gather the tag set.

        :return: A list that contains the existing tags on the object in the S3 bucket
        """
        try:
            response = s3_client.get_object_tagging(Bucket=self.src_bucket, Key=self.object_key)
        except ClientError as err:
            print(f'failed to get existing tags: {str(err)}')
        else:
            return [f'{tag["Key"]}={tag["Value"]}' for tag in
                    response['TagSet'] if not tag['Key'].startswith(FSS_TAG_PREFIX)]

    def _copy_object(self, dst_bucket: str, acl: str = None) -> None:
        """
        Private method that makes AWS API call to move an object from one S3 location to another.

        This is a managed transfer that will perform a multipart copy in multiple threads if necessary.
        Will check for existing metadata on the S3 object to be added and checks if an ACL should be applied to object.

        :param dst_bucket: (required) A string value that is the ARN of the S3 bucket where the object will be moved
        :param acl: (optional) A string value of an ACL to be applied to the S3 object
        :return: None
        """
        params = {
            'TaggingDirective': 'REPLACE',
            'Tagging': '&'.join(self.tag_list),
            **(self.metadata if self.metadata else {})
        }

        copy_source = {
            'Bucket': self.src_bucket,
            'Key': self.object_key
        }

        if acl and acl in VALID_ACL:
            params['ACL'] = acl

        try:
            s3_client.copy(copy_source, dst_bucket, self.object_key, params, Config=transfer_config)
        except ClientError as err:
            print(f'failed to copy object with error: {str(err)}')

    def _tag_object(self) -> None:
        """
        Private method that will tag an existing object in a bucket.

        Used for situations where the object will not be copied to another bucket after operation.
        Will tag the scanned object in place with the created tag set.

        :return: None
        """
        tag_set = []
        for tag in self.tag_list:
            attrs = tag.split('=')
            tag_set.append({'Key': attrs[0], 'Value': attrs[1]})

        try:
            s3_client.put_object_tagging(
                Bucket=self.src_bucket,
                Key=self.object_key,
                Tagging=
                {
                    'TagSet': tag_set
                })
        except ClientError as err:
            print(f'failed to tag object(s) {self.object_key} in bucket {self.src_bucket} with error {err}')

    def _delete_objects(self, prefix: str, objects: List[str]) -> None:
        """
        Private method that will call AWS API and delete multiple objects in a single request if necessary.

        Will use Python dict comprehension to create necessary format to delete objects.
        {'Objects': ['Key': 'string', 'VersionId': 'string',]}

        :param prefix: (required) A string value that determines which objects will be deleted
        :param objects: (required) A list containing string values of the object key(s) for the objects to be deleted
        :return: None
        """
        objects = {'Objects': [{'Key': prefix + obj} for obj in objects]}
        try:
            s3_client.delete_objects(Bucket=self.src_bucket, Delete=objects)
        except ClientError as err:
            print(f'failed to delete object(s): {objects} due to error: {str(err)}')

    def run(self, mode: str, dst_bucket: str, acl: str = None) -> None:
        """
        Public method used to dispatch calls to private methods.

        Will check to see if any existing tags exist on the object (excluding FSS tags) and add them
        to the tag list being applied to the object.

        Will check to see what mode was selected by the user, 'copy' or 'move' and decide whether a
        'delete' operation is necessary.

        :param mode: (required) A string value that depicts the want of the user on how to handle scan results
        :param dst_bucket: (required) A string value that maps to the ARN of the destination bucket to objects (promote/quarantine)
        :param acl: (optional) A string value that will dictate a specific ACL applied to an object
        :return: None
        """
        self._parse_s3_object_url()
        self._create_tags()
        self._get_metadata()
        if existing_tag_set := self._get_existing_tag_set():
            self.tag_list.extend(existing_tag_set)

        if not dst_bucket:
            print(f'Tagging in place object: {self.object_key} in bucket: {self.src_bucket}')
            self._tag_object()
            return

        self._copy_object(dst_bucket, acl)

        if mode == 'move':
            self._delete_objects(prefix='', objects=[self.object_key])


def lambda_handler(event, context) -> None:
    """
    AWS Lambda handler that takes a trigger event from SNS topic.

    :param event: (required) An event coming from SNS that contains results of S3 object scan
    :param context: (required) The Lambda runtime context created an invocation
    :return: None
    """

    # collect the ENV vars
    acl = os.getenv('ACL')
    quarantine_bucket = os.getenv('QUARANTINEBUCKET')
    quarantine_mode = get_mode_from_env('QUARANTINEMODE')
    promote_bucket = os.getenv('PROMOTEBUCKET')
    promote_mode = get_mode_from_env('PROMOTEMODE')

    # start main event loop
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        message_data = ObjectData(message)
        if message_data.scanner_status:
            print(f'Skip: {message_data.scanner_status_message}')
            continue
        tagging = AssignTag(message_data)

        # ternary expressions that decided whether the object is promoted or quarantined
        operation = 'quarantine' if message_data.findings else 'promotion'
        mode = quarantine_mode if message_data.findings else promote_mode
        dst_bucket = quarantine_bucket if message_data.findings else promote_bucket

        if not dst_bucket:
            print(f'Skip: No bucket specified for {operation} in mode: {mode}')

        tagging.run(mode, dst_bucket, acl)
        print(f'File {operation} successful (mode: {mode})') if dst_bucket else print('File tagged in place')
