import logging
import urllib3
import json
import os
http = urllib3.PoolManager()
import azure.functions as func

# Hide verbose HTTP logging
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)


def main(message: func.ServiceBusMessage):
    # set teams variables
    url = os.environ['TEAMS_URL_WEBHOOK']
    account = os.environ["TENANT_NAME"]

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
            
        malwares=', '.join(malwares)
        types=', '.join(types)  
        file_url=str(message['file_url'])
            
        payload = {
            "summary":"Malicious Object Detected",   
            "sections":[
                {
                    "activityTitle":"A <b>Malicious object</b> has been detected!"
                },
                {
                    "markdown": False,
                    "facts":[
                        {
                            "name":"Azure Tenant:",
                            "value":account
                        },
                        {
                            "name":"Malware Name(s):",
                            "value":malwares
                        },
                        {
                            "name":"Malware Type(s):",
                            "value":types
                        },
                        {
                            "name":"File URL:",
                            "value":file_url
                        }
                    ]
                }
            ]
        }
        
        encoded_msg = json.dumps(payload).encode('utf-8')
        resp = http.request('POST',url, body=encoded_msg)
        logging.info(f'sending ms teams response: {resp}')
