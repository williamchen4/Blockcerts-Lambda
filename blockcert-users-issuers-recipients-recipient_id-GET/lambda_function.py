import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableUsers = dynamodb.Table('blockcert.users')
tableInvites = dynamodb.Table('blockcert.invites')
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
    
    # get user's username
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/login/?token=" + token
    response = requests.post(url, params = {'Admin':True})
    json_data = json.loads(response.text)
    
    username = json_data.get('username')
    
    issuerIDs = []
    response = tableUsers.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('email') == username:
            issuerIDs = resp_dict.get('issuers')
            break
    
    recipientID = event['params']['path']['recipient_id']
    unmatchedIssuers = []
    unmatchedIssuersNamed = []
    
    response = tableInvites.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if (resp_dict.get('issuer_id') in issuerIDs) and recipientID == resp_dict.get('recipient_id'):
            unmatchedIssuers.append(resp_dict.get('issuer_id'))
    
    response = tableIssuers.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') in unmatchedIssuers:
            unmatchedIssuersNamed.append({"id":resp_dict.get('id'), "name":resp_dict.get('name')})

    return unmatchedIssuersNamed
    