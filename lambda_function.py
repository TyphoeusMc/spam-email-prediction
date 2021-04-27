import json
import os
import boto3
from botocore.exceptions import ClientError
# header for formating data for prediction
from sms_spam_classifier_utilities import one_hot_encode
from sms_spam_classifier_utilities import vectorize_sequences
# some global data
vocabulary_length = 9013
endpoint_name = 'spam-email-predict-mtf-ymj'

def lambda_handler(event, context):
    '''
    # first fetch email object from s3
    s3 = event['Records'][0]['s3']
    bucket = s3['bucket']['name']
    key = s3['object']['key']
    # code is modified from assignment2
    s3_bucket = boto3.resource('s3')
    object = s3_bucket.Object(bucket, key)
    # now we get a stream object
    res = object.get()
    streamObject = res['Body']
    dataString = streamObject.read()
    streamObject.close()
    # print(dataString)
    
    # info to get from the dataString: sender, subject and body
    # be aware that line changing may happen every where
    data_elements = dataString.decode().split('\r\n')
    sender = 'eee'
    subject = ''
    content = ''
    # 0: other, 1: sender, 2: subject, 3: content
    current_state = 0
    for line in data_elements:
        if len(line) >= 1:
            # detect sender
            if line.startswith("From:"):
                current_state = 1
                sender = (line.split(':')[1]).strip(' ')
            elif line.startswith("Subject:"):
                current_state = 2
                subject = (line.split(':')[1]).strip(' ')
            elif line.startswith("To:") or line.startswith("MIME-Version:"):
                current_state = 0
            elif line.startswith("X-SES-Outgoing:"):
                current_state = 3
            else:
                if current_state == 1:
                    sender += line
                elif current_state == 2:
                    subject += line
                elif current_state == 3:
                    content += line.strip('=')
                # else: do nothing
    print(content)
    
    
    
    # client = boto3.client('sagemaker')
    # response = client.list_endpoints()
    # print(response)
    # delete existing endpoint
    # for ep in response['Endpoints']:
        # client.delete_endpoint(EndpointName = ep['EndpointName'])
    # response = client.list_endpoints()
    
    
    
    # sending message to the endpoint
    
    email_content_to_send = [content]
    one_hot_test_messages = one_hot_encode(email_content_to_send, vocabulary_length)
    encoded_test_messages = vectorize_sequences(one_hot_test_messages, vocabulary_length)
    
    runtime= boto3.client('runtime.sagemaker')
    payload = json.dumps(encoded_test_messages.tolist())
    response = runtime.invoke_endpoint(EndpointName = endpoint_name,
                                       ContentType = 'application/json',
                                       Body = payload)
    streamObject = response['Body']
    result_data = json.loads(streamObject.read().decode())
    streamObject.close()
    # print(result_data)
    # result format: {"predicted_probability": [[0.00027317210333421826]], "predicted_label": [[0.0]]}
    label = result_data["predicted_label"][0][0]
    '''
    # now we can send email back to sender
    
    # SEND EMAIL TEST
    
    SENDER = "Sender Name <maitingfeng@anxiangongyu.cn>"
    RECIPIENT = "tm3358@nyu.edu"
    # CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "us-east-1"
    SUBJECT = "spam email detect result"
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                )
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name = AWS_REGION)
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination = {
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message = {
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source = SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
