import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableUsers = dynamodb.Table('blockcert.users')
tableInvites = dynamodb.Table('blockcert.invites')
tableIssuers = dynamodb.Table('blockcert.issuers')
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
    
    # get issuers that user has access to
    issuerIDs = []
    response = tableUsers.scan()
    for i in response['Items']:
        if i['email'] == event['params']['path']['id']:
            issuerIDs += (i['issuers'])
            issuerIDs += (i['ownedIssuers'])
            break

    recipientID = event['params']['path']['recipient_id']
    
    # get recipient ID if email passed    
    if (recipientID.isdigit() == False):
        response = tableRecipients.scan()
        for i in response['Items']:
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('email') == recipientID:
                recipientID = resp_dict.get('id')
                break
    
    unmatchedIssuers = []
    unmatchedIssuersNamed = []
    response = tableInvites.scan()
    for i in response['Items']:
        if i['issuer_id'] in issuerIDs and recipientID == i['recipient_id']:
            unmatchedIssuers.append(i['issuer_id'])

    for issuer in unmatchedIssuers:
        tableBody = tableIssuers.query(KeyConditionExpression=Key('id').eq(issuer))
        unmatchedIssuersNamed.append({"id":tableBody['Items'][0]['id'], "name":tableBody['Items'][0]['name']})

    return unmatchedIssuersNamed
    