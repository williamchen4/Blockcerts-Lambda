import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRevocations = dynamodb.Table('blockcert.revocations')
tableIssuers = dynamodb.Table('blockcert.issuers')

def lambda_handler(event, context):
    
    # Check if Issuer ID exists
    issuerID = event['params']['id']
    tableBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(issuerID)
    )
    if tableBody['Count'] == 0:
        return 'Error: ID does not exist'
    
    revocationID = str(uuid.uuid4())

    data = {
        "id": "http://blockcerts.fresnostate.edu/issuers/" + issuerID + "/revocations/" + revocationID,
        "issuer_id": issuerID,
        "cert_id": event['params']['uuid'],
        "reason": event['body']['reason']
    }
    
    tableRevocations.put_item(Item = data)
    
    return {
        "Status":"200 OK"
    }