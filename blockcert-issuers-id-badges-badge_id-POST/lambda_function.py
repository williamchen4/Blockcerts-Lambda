import json
import boto3
import random
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableBadges = dynamodb.Table('blockcert.badges')
tableIssuers = dynamodb.Table('blockcert.issuers')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
        
def lambda_handler(event, context):

    # check if issuer ID exists
    issuerID = event['params']['id']
    tableBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(issuerID)
    )
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "Issuer does not exist"
        })
        
    # check if empty image
    if event['body']['image'] == None:
        raise Exception({
            "errorType":"Empty",
            "httpStatus":400,
            "message":"Empty Field"
        })   
    
    # check empty fields
    for i in event['body']:
        if len(event['body'][i]) == 0:
            raise Exception({
                "errorType" : "Empty",
                "httpStatus": 400,
                "message": "Empty Field"
             })
             
    for i in event['body']['signatureLines']:
        if ((len(i.get('name')) == 0)  or (i.get('image') == None) or (i.get('image') == "") or (len(i.get('jobTitle')) == 0)):
            raise Exception({
                "errorType" : "Empty",
                "httpStatus": 400,
                "message": "Empty Field"
            })

    # check existing badge name
    response = tableBadges.scan()
    for i in response['Items']: 
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if(event['params']['badge_id'] != resp_dict.get('id') and issuerID == resp_dict.get('issuer_id') and event['body']['name'] == resp_dict.get('name')):
            raise Exception({
                "errorType" : "Conflict",
                "httpStatus": 409,
                "message": "Badge name already exists"
            })
    
    # create data for DynamoDB
    data = {
        "id": event['params']['badge_id'],
        "issuer_id": issuerID,
        "name": event['body'].get('name'),
        "description": event['body'].get('description'),
        "criteria": {
            "narrative": event['body'].get('criteria').get('narrative')
        },
        "image": event['body'].get('image'),
        "signatureLines": event['body'].get('signatureLines'),
        "template":event['body'].get('template')
        }
        
    tableBadges.put_item(Item=data)
    
    return {
        "Status":"200 OK"
    }