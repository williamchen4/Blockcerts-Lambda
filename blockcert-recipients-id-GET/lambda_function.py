import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

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

    pID = event['params']['id']
    exists = False

    response = table.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') == pID or resp_dict.get('email') == pID:
            exists = True
            break
    
    if exists == False:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404
        })
    
    
    addresses = []

    for i in resp_dict.get('addresses'):
        for i2 in i.keys():
            addresses.append({
                "id":i2,
                "address":i[i2]
            })
    resp_dict['addresses']=addresses
    return resp_dict