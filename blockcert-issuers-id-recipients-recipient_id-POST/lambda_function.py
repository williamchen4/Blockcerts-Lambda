import json
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableInvites = dynamodb.Table('blockcert.invites')
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
    
    # get parameters
    issuerID = event['params']['path']['id']
    recipientID = event['params']['path']['recipient_id']
    badgeList = []
    
    # get recipient ID if email passed    
    if (recipientID.isdigit() == False):
        response = tableRecipients.scan()
        for i in response['Items']:
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('email') == recipientID:
                recipientID = resp_dict.get('id')
                break
    
    # remove previous "active" nonce
    response = tableInvites.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if recipientID == resp_dict.get('recipient_id') and issuerID == resp_dict.get('issuer_id'):
            tableInvites.delete_item(Key={"id":resp_dict.get('id')})
            badgeList = resp_dict.get('badges')
            break

    # send new email to recipient
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/recipients/" + recipientID + "/invite/" + issuerID
    j = json.dumps(badgeList)
    requests.post(url, data=j).json()
    return "Invite sent to " + recipientID