import json
import boto3
from botocore.exceptions import ClientError

step_client = boto3.client('stepfunctions')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableTest = dynamodb.Table('test')

def lambda_handler(event, context):
    print('Event data:')
    print(event)

    '''
    data = []
    for i in event:
        data.append({
            'recipientName':i['recipientName'],
            'recipientEmail':i['recipientEmail'],
            'fileID':i['fileID']
        })
    '''
    payload = {
        'payload':event
    }
    try:
        step_client.start_execution(
            stateMachineArn='arn:aws:states:us-west-2:010063476047:stateMachine:AwardEmails',
            input = json.dumps(payload)
        )
    except Exception as e:
        test.put_item({'id':str(e)})