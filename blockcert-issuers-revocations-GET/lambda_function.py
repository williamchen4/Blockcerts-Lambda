import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.revocations')

def lambda_handler(event, context):
    pID = event['params']['id']
    tableBody = table.query(
    KeyConditionExpression=Key('uuid').eq(pID)
    )
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType":Exception,
            "httpStatus":404,
            "message":"Issuer does not exist"
        })
    return tableBody['Items'][0]
