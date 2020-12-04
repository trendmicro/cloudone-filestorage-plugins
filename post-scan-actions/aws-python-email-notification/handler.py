import json
import os
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    sender = os.environ['SENDER']
    recipient = os.environ['RECIPIENT']    
    aws_region = os.environ['AWS_REGION']
    subject = os.environ['SUBJECT']
    charset = "UTF-8"

    for record in event['Records']:

        # Analyze the message and look for findings
        message = json.loads(record['Sns']['Message'])
        findings = message['scanning_result'].get('Findings')

        if findings:

            body_text = '''\
                CloudOne FSS Email Notification
                File URL: {file_url}\
                '''.format(file_url=str(message['file_url']))
            for finding in message['scanning_result']['Findings']:
                body_text = body_text + '''\
                    Malware: {malware}
                    Type: {type}\
                    '''.format(malware=str(finding.get('malware')),
                               type=str(finding.get('type')))

            body_html = '''\
                <html><head></head><body><h1>CloudOne FSS Email Notification</h1><p>
                <p><b>File URL: </b>{file_url}</p>\
                '''.format(file_url=str(message['file_url']))
            for finding in message['scanning_result']['Findings']:
                body_html = body_html + '''\
                    <p><b>Malware: </b>{malware}</p>
                    <p><b>Type: </b>{type}</p>
                    </html></body></p>\
                    '''.format(malware=str(finding.get('malware')),
                               type=str(finding.get('type')))

            # Create a new SES resource and specify a region.
            client = boto3.client('ses',region_name=aws_region)
            
            # Try to send the email.
            try:
                response = client.send_email(
                    Destination={
                        'ToAddresses': [
                            recipient,
                        ],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset': charset,
                                'Data': body_html,
                            },
                            'Text': {
                                'Charset': charset,
                                'Data': body_text,
                            },
                        },
                        'Subject': {
                            'Charset': charset,
                            'Data': subject,
                        },
                    },
                    Source=sender,
                )
            # Display an error if something goes wrong.	
            except ClientError as e:
                print(json.dumps(e.response['Error']['Message']))
                return
            else:
                print("Email sent! Message ID:"+response['MessageId'])
                return

    print("Nothing done.")
