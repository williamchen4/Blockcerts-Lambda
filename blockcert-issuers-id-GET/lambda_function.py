import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableIssuers = dynamodb.Table('blockcert.issuers')
tableUsers = dynamodb.Table('blockcert.users')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    
    # Check if Issuer ID exists
    pID = event['params']['path']['id']
    tableBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(pID)
    )
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Issuer ID does not exist"
        })

    # Search for current active key
    active_public_key = 1
    active_private_key = 1
    active_created = 1
    
    mList = []
    response = tableIssuers.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') == pID:
            mList.append(resp_dict.get('key_info'))

    for i in mList[0]:
        if "revoked" not in i:
            active_public_key = i["public_key"]
            active_private_key = i["private_key"]
            active_created = i["created"]
            break

    publicKey = tableBody['Items'][0].get('public_key')
    image = tableBody['Items'][0].get('image')
    email = tableBody['Items'][0].get('email')
    data = {
        "@context": [
            "https://w3id.org/openbadges/v2",
            "https://w3id.org/blockcerts/v2"
            ],
        "type": "Profile",
        "id": pID,
        "name": tableBody['Items'][0].get('name'),
        "url": tableBody['Items'][0].get('url'),
        "introductionURL": str("https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + pID + "/intro"),
        "publicKey": [
                {
                    "id": str(active_public_key),
                    "created": str(active_created)
                }
        ], 
        "revocationList": "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + pID + "/revocations",
        "image": tableBody['Items'][0].get('image'),
        "email": tableBody['Items'][0].get('email')
    }

    # if call made by admin or owner of issuer, return private key as well
    if "Authorization" in event['params']['header']:
        token = event['params']['header']['Authorization'][7:]
        url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
        headers = {"Authorization":event['params']['header']['Authorization']}
        response = requests.get(url, headers=headers)
        json_data = json.loads(response.text)

        if 'Admin' in json_data['cognito:groups']:
            data['privateKey'] = str(active_private_key)
        
        # check if owner has access to view private key
        elif 'Owner' in json_data['cognito:groups']:
            response = tableUsers.scan()
            for i in response['Items']:
                json_str = json.dumps(i, cls=DecimalEncoder)
                resp_dict = json.loads(json_str)
                if resp_dict.get('email') == json_data['username']:
                    if pID in resp_dict.get('ownedIssuers'):
                        data['privateKey'] = str(active_private_key)
                        break
        data['owner'] = tableBody['Items'][0].get('owner')
    return data
