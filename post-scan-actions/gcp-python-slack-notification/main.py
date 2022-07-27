import os
import base64
import json
import textwrap
import urllib3
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

        url = os.environ['SLACK_URL']
        channel = os.environ['SLACK_CHANNEL']
        username = os.environ['SLACK_USERNAME']

        # Context: {event_id: 5201641954693584, timestamp: 2022-07-27T17:03:42.432Z, event_type: providers/cloud.pubsub/eventTypes/topic.publish, resource: projects/gcp-fss/topics/jasondablow-scan-result-topic}
        print("""This Function was triggered by messageId {} published at {} to {}""".format(context.event_id, context.timestamp, context.resource))

        # {'timestamp': 1658940543.4881084, 'file_url': 'https://storage.googleapis.com/fss-jason/eicar', 'scan_start_timestamp': 1658940543.3512957, 'scanner_status': 0, 'scanner_status_message': 'successful scan', 'scanning_result': {'TotalBytesOfFile': 68, 'Findings': [{'malware': 'Eicar_test_file', 'type': 'Virus'}], 'Error': '', 'Codes': []}}

        if message:
            # Message details from the Pub/Sub topic publish event
            findings = message['scanning_result'].get('Findings')

            if findings:

                project_id = get_gcp_project_id(resource_name=context.resource)
                bucket_name = get_bucket_name_from_file_url(file_url=str(message['file_url']))
                file_name = get_file_name_from_file_url(file_url=str(message['file_url']))

                malwares = []
                types = []
                for finding in message['scanning_result']['Findings']:
                    malwares.append(finding.get('malware'))
                    types.append(finding.get('type'))

                body_text = textwrap.dedent('''
                    Malware Detected!

                    GCP Project ID: {project_id}
                    GCP Bucket Name: {bucket_name}
                    File Name: {file_name}
                    Malware Name(s): {malwares}
                    Malware Type(s): {types}
                    File URL: {file_metadata_url}
                ''').format(
                    project_id=project_id,
                    bucket_name=bucket_name,
                    file_name=file_name,
                    malwares=', '.join(malwares),
                    types=', '.join(types),
                    file_metadata_url=str(build_file_metadata_url(project_id=project_id, bucket_name=bucket_name, file_name=file_name))
                )

                payload = {
                    "channel": channel,
                    "username": username,
                    "text": body_text,
                    "icon_emoji": ":rotating_light:"
                }

                encoded_message = json.dumps(payload).encode('utf-8')
                resp = http.request('POST', url,  body=encoded_message)
                return resp.status

    except Exception as e:
        print("Error: ", str(e))
