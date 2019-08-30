import json
import boto3

client = boto3.client('stepfunctions')

def lambda_handler(event, context):
    
    data = {
        "init":1,
        "foo":2
    }
     
    response = client.start_execution(
        stateMachineArn='arn:aws:states:us-west-2:010063476047:stateMachine:test1',
        input = json.dumps(data)
    )