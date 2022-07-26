import os
import base64
import json
import textwrap
import urllib3
http = urllib3.PoolManager()

def main(event, context):

    print(f'Context: {context}')
    base64_data = event.get('data', '')
    base64_bytes = base64_data.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = json.loads(message_bytes.decode('ascii'))
    print(f'Message: {message}')

    url = os.environ['SLACK_URL']
    channel = os.environ['SLACK_CHANNEL']
    username = os.environ['SLACK_USERNAME']

    print("""This Function was triggered by messageId {} published at {} to {}""".format(context.event_id, context.timestamp, context.resource["name"]))

    for detection in message:

        # Message details from the Pub/Sub topic publish event
        msg = json.loads(detection)
        findings = msg['scanning_result'].get('Findings')

        # get GCP Project ID
        arn = json.dumps(detection)
        account_id = arn.split(":")[4].strip()

        if findings:

            malwares = []
            types = []
            for finding in msg['scanning_result']['Findings']:
                malwares.append(finding.get('malware'))
                types.append(finding.get('type'))

            body_text = textwrap.dedent('''
            WARNING
            AWS Account ID: {account}
            File URL: {file_url}
            Malware Name(s): {malwares}
            Malware Type(s): {types}
            ''').format(
            account=str(account_id),
            file_url=str(msg['file_url']),
            malwares=', '.join(malwares),
            types=', '.join(types)
            )

            payload = {
                "channel": channel,
                "username": username,
                "text": body_text,
                "icon_emoji": ":rotating_light:"
            }

            encoded_msg = json.dumps(payload).encode('utf-8')
            resp = http.request('POST', url,  body=encoded_msg)
            return resp.status
