import logging
import os
import json
import urllib3
http = urllib3.PoolManager()
import textwrap

import azure.functions as func
from azure.identity import DefaultAzureCredential

# Hide verbose HTTP logging
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)


def main(message: func.ServiceBusMessage):
    # set slack variables
    url = os.environ["SLACK_URL_WEBHOOK"]
    account = os.environ["SUB_NAME"]
    channel = os.environ["SLACK_CHANNEL"]

    # Log the Service Bus Message as plaintext
    message_body = message.get_body().decode("utf-8")
    logging.info('Python ServiceBus topic trigger processed message.')
    logging.info(f'Message Body: {message_body}')

    message = json.loads(message_body)
    findings = message['scanning_result'].get('Findings')

    if findings:         
        malwares = []
        types = []
        for finding in findings:
            malwares.append(finding.get('malware'))
            types.append(finding.get('type'))

        body_text = textwrap.dedent('''
        WARNING
        Azure Subscription: {account_id}
        File URL: {file_url}
        Malware Name(s): {malwares}
        Malware Type(s): {types}
        ''').format(
        account_id=str(account),
        file_url=str(message['file_url']),
        malwares=', '.join(malwares),
        types=', '.join(types)
        )
            
        payload = {
                    "channel": channel,
                    "text": body_text,
                    "icon_emoji": ":rotating_light:"
                    }
        
        encoded_msg = json.dumps(payload).encode('utf-8')
        resp = http.request('POST', url, body=encoded_msg)
        logging.info(f'sending slack response: {resp}')
