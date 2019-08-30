import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.revocations')
tableIssuers = dynamodb.Table('blockcert.issuers')

def lambda_handler(event, context):
    
    # Check if Issuer ID exists
    issuerID = event['params']['id']
    tableBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(issuerID)
    )
    if tableBody['Count'] == 0:
        return 'Error: Issuer ID does not exist'
    
    revocationID = "http://blockcerts.fresnostate.edu/issuers/" + issuerID + "/revocations/" + event['params']['uuid']
    
    tableBody = table.query(
    KeyConditionExpression=Key('id').eq(event['params']['uuid'])
    )
    if tableBody['Count'] == 0:
        return {
            "Error": "Cert " + event['params']['uuid'] + " is not revoked"
        }
     
    data = {
        "@context": "https://w3id.org/openbadges/v2",
        "id": revocationID,
        "type": "RevocationList",
        "issuer": "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + issuerID,
        "revokedAssertions": [
            { 
                "id": "urn:uuid:" + event['params']['uuid'],
                "revocationReason": tableBody['Items'][0]["reason"]
            }
        ]
    }
    return data