import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests
import re

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')
lambda_client = boto3.client('lambda')
step_client = boto3.client('stepfunctions')

def lambda_handler(event, context):

    # check if no recipients
    if len(event['body-json']) == 0:
        raise Exception({
            "errorType" : "Empty",
            "httpStatus": 400,
            "message": "Empty Field"
        })
    # check file formatted correctly
    if len(event['body-json']) % 3 != 0:
        raise Exception({
            "errorType" : "Empty",
            "httpStatus": 400,
            "message": "File formatted incorrectly"
        })

    payload = {}
    payload['data'] = event['body-json']
    payload['issuerID'] = event['params']['path']['id']
    payload['badgeID'] = event['params']['path']['badge_id']
    
    # async call
    invoke_response = lambda_client.invoke(
        FunctionName="blockcert-issuers-id-badges-badge_id-async_issue-POST", 
        InvocationType='Event', Payload=json.dumps(payload))

    #return invoke_response['Payload'].read()
    return 200