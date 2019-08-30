import json
import boto3
import random
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.recipients')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):

    # check no empty fields
    if len(event['name']) == 0 or len(event['email']) == 0:
        raise Exception({
            "errorType" : "Empty",
            "httpStatus": 400,
            "message": "Empty Field"
        })
    
    # check if recipient already exists
    response = table.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('email') == event['email']:
            raise Exception({
                "errorType" : "Conflict",
                "httpStatus": 409,
                "message": "Recipient already exists"
            })
     
    # create randomized recipient ID
    pID = random.randint(10000, 99999)
    tableBody = table.query(
    KeyConditionExpression=Key('id').eq(str(pID))
    )
    while tableBody['Count'] != 0:
        pID = random.randint(10000, 99999)
        tableBody = table.query(
        KeyConditionExpression=Key('id').eq(str(pID))
        )
        
    # update blockcert.recipients
    event['id'] = str(pID)
    event['certs'] = []
    event['addresses'] = []
    table.put_item(Item=event)
    
    return { "id":str(pID) }
