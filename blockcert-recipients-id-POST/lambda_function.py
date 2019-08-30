import json
import boto3
from datetime import datetime
from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
        
def lambda_handler(event, context):

    # check if recipient ID exists
    tableBody = tableRecipients.query(KeyConditionExpression=Key('id').eq(event['params']['id']))
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "Recipient does not exist"
            })
    
    # check for empty fields
    if len(event['body']['name']) == 0 or len(event['body']['email']) == 0:
        raise Exception({
            "errorType" : "Empty",
            "httpStatus": 400,
            "message": "Empty Field"
        })
    
    # check for existing recipient email
    response = tableRecipients.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') != event['params']['id'] and resp_dict.get('email') == event['body']['email']:
            raise Exception({
                "errorType" : "Conflict",
                "httpStatus": 409,
                "message": "Recipient email already taken"
            })
    
    # update blockcert.recipients
    event['body']['id'] = str(event['params']['id'])
    event['body']['addresses'] = tableBody['Items'][0]['addresses']
    event['body']['certs'] = tableBody['Items'][0]['certs']
    tableRecipients.put_item(Item=event['body'])
    return {
        "Status":"200 OK"
    }