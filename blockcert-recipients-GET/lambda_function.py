import boto3
import json
import decimal
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
    
    # return autocomplete ID/email
    if event['params']['querystring'] != {}:
        startingID = event['params']['querystring']['query']
        
        mList = []
        response = table.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('id').startswith(startingID):
                mList.append(resp_dict.get('id'))
            elif resp_dict.get('email').startswith(startingID):
                mList.append(resp_dict.get('email'))
        mList.sort()
        return mList
    
    if event['params']['querystring'] != 'none':
        # return list of IDs and emails
        mList = []
        response = table.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            mList.append(resp_dict.get('id'))
            mList.append(resp_dict.get('email'))
    
        return mList