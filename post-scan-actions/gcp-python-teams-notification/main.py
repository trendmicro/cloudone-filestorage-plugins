import os
import json
import base64
import urllib3
from http.client import responses

http = urllib3.PoolManager()

def get_gcp_project_id(resource_name):
    return str(resource_name).split("/")[1]

def get_bucket_name_from_file_url(file_url):
    return str(file_url.split("/")[-2:][0])

def get_file_name_from_file_url(file_url):
    return str(file_url.split("/")[-1:][0])

def build_file_metadata_url(project_id, bucket_name, file_name):
    return "https://console.cloud.google.com/storage/browser/_details/" + bucket_name + "/" + file_name + "?project=" + project_id

def main(event, context):

    try:

        print(f'Context: {context}')
        print(f'Event: {event}')
        base64_data = event.get('data', '')
        base64_bytes = base64_data.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = json.loads(message_bytes.decode('ascii'))
        print(f'Message: {message}')

        url = os.environ['TEAMS_URL']

        print("""This Function was triggered by messageId {} published at {} to {}""".format(context.event_id, context.timestamp, context.resource))

        if message:
            # Message details from the Pub/Sub topic publish event
            findings = message['scanning_result'].get('Findings')

            if findings:

                project_id = get_gcp_project_id(resource_name=context.resource)
                bucket_name = get_bucket_name_from_file_url(file_url=str(message['file_url']))
                file_name = get_file_name_from_file_url(file_url=str(message['file_url']))
                file_metadata_url=str(build_file_metadata_url(project_id=project_id, bucket_name=bucket_name, file_name=file_name))

                malwares = []
                types = []
                for finding in message['scanning_result']['Findings']:
                    malwares.append(finding.get('malware'))
                    types.append(finding.get('type'))

                malwares=', '.join(malwares)
                types=', '.join(types)

                payload = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    'summary': 'Malicious Object Detected',
                    'sections': [
                        {
                            'activityTitle': 'A <b>Malicious object</b> has been detected!'
                        },
                        {
                            'markdown': False,
                            'facts': [
                                {
                                    'name': 'GCP Project ID: ',
                                    'value': project_id
                                },
                                {
                                    'name': 'GCP Bucket Name: ',
                                    'value': bucket_name
                                },
                                {
                                    'name': 'File Name: ',
                                    'value': file_name
                                },
                                {
                                    'name': 'Malware Name(s): ',
                                    'value': malwares
                                },
                                {
                                    'name': 'Malware Type(s): ',
                                    'value': types
                                },
                                {
                                    'name': 'File URL: ',
                                    'value': file_metadata_url
                                }
                            ]
                        }
                    ],
                    'potentialAction': [
                        {
                            '@type': 'OpenUri',
                            'name': 'View File Metadata',
                            'targets': [
                                {
                                    'os': 'default',
                                    'uri': file_metadata_url
                                }
                            ]
                        }
                    ]
                }

                encoded_message = json.dumps(payload).encode('utf-8')
                resp = http.request('POST', url,  body=encoded_message)

                if resp.status != 200:
                    raise Exception("HTTP Error " + str(resp.status) + ". Message: " + str(responses[resp.status]))
                return resp.status

    except Exception as e:
        print("Error: ", str(e))
