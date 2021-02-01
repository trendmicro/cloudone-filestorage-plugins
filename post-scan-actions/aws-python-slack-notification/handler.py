import urllib3
import json
import os
http = urllib3.PoolManager()
import textwrap

def lambda_handler(event, context):

    url = os.environ['SLACK_URL']
    channel = os.environ['SLACK_CHANNEL']
    username = os.environ['SLACK_USERNAME']
    
    for record in event['Records']:

        #Message details from SNS event
        message = json.loads(record['Sns']['Message'])
        findings = message['scanning_result'].get('Findings')

        #ARN info to get AWS Account ID
        arn = json.dumps(record['EventSubscriptionArn'])
        account_id = arn.split(":")[4].strip()

        if findings:
        
            malwares = []
            types = []
            for finding in message['scanning_result']['Findings']:
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
            file_url=str(message['file_url']),
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
            resp = http.request('POST',url, body=encoded_msg)