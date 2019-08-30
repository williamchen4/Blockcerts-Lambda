import json
import boto3
import random
import uuid
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
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Issuer does not exist"
        })
    
    # check if empty image
    if event['body']['image'] == None:
        raise Exception({
            "errorType":"Empty",
            "httpStatus":400,
            "message":"Empty Field"
        })     
    
    # check empty fields

    if ((len(event['body']['signatureLines'][0].get('name')) == 0)  or ((event['body']['signatureLines'][0].get('image')) == (None or "")) or (len(event['body']['signatureLines'][0].get('jobTitle')) == 0)):
        raise Exception({
            "errorType" : "Empty",
            "httpStatus": 400,
            "message": "Empty Field"
        })
        
    for i in event['body']:
        if len(event['body'][i]) == 0:
            raise Exception({
                "errorType":"Empty",
                "httpStatus":400,
                "message":"Empty Field"
             })
             


    response = tableBadges.scan()

    # check existing badge name
    for i in response['Items']: 
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if(issuerID == resp_dict.get('issuer_id') and event['body']['name'] == resp_dict.get('name')):
            raise Exception({
                "errorType" : "Conflict",
                "httpStatus": 409,
                "message": "Badge name already exists"
            })
        
    # get previous largest ID
    mList = []
    for i in response['Items']: 
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        mList.append(resp_dict.get('id'))
        
    # create badge ID
    prevID = 0
    for i in mList:
        if prevID < int(i):
            prevID = int(i)
    newID = prevID + 1
    badgeID = str(newID)

    # create data for DynamoDB
    data = {
        "id": badgeID,
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