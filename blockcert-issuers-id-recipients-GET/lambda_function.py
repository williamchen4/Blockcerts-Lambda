import json
import boto3
from datetime import datetime
from datetime import date
from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr
import dateutil.parser as parser
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
    mList = []
    issuerID = event['params']['path']['id']
    response = table.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        for address in resp_dict.get('addresses'):
            if issuerID in address:
                mList.append(resp_dict.get('id'))
    return mList