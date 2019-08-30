import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.users')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
    
def lambda_handler(event, context):

    # check admin status
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/login/?token=" + token
    response = requests.post(url, params = {'Admin':True})
    json_data = json.loads(response.text)

    if json_data == False:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 401,
        })
        
    # Return list of users that can manage this issuer
    issuerID = event['params']['path']['id']
    allowedUsers = []
    unallowedUsers = []
    response = table.scan()
    for i in response['Items']: 
        if issuerID in i['issuers']:
            allowedUsers.append(i['id'])
        else:
            unallowedUsers.append(i['id'])
            
    allowedUsers.sort()
    unallowedUsers.sort()
    return {
        "allowedUsers":allowedUsers,
        "unallowedUsers":unallowedUsers
    }    