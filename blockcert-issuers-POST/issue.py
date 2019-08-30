import json
import boto3
import random
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from io import BytesIO
from botocore.vendored import requests
import pytz
from pytz import timezone

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.issuers')
tableUsers = dynamodb.Table('blockcert.users')
client = boto3.client('s3')

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
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)

    if 'Manager' in json_data['cognito:groups']:
        raise Exception({
            "errorType" : "Authorization",
            "httpStatus": 401,
            "message":"User is unauthorized"
        })
        
    # check empty image
    if event['body-json']['image'] == None:
        raise Exception({
            "errorType" : "Empty",
            "httpStatus": 400,
            "message": "Empty Field"
        })
        
        
    # check empty fields
    for i in event['body-json']:
        if len(event['body-json'][i]) == 0:
            raise Exception({
                "errorType" : "Empty",
                "httpStatus": 400,
                "message": "Empty Field"
            })
    
    response = table.scan()

    # check existing name
    for i in response['Items']: 
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('name') == event['body-json']['name']:
            raise Exception({
                "errorType" : "Conflict",
                "httpStatus": 409,
                "message": "Issuer name already exists"
            })        
    
    
    # get previous largest ID
    response = table.scan()

    mList = []
    for i in response['Items']: 
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        mList.append(resp_dict.get('id'))
    
    # create new ID
    prevID = 0
    for i in mList:
        if prevID < int(i):
            prevID = int(i)
    newID = prevID + 1

    # set Pacific time
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
         
    data = {
        "id":str(newID),
        "name":event['body-json']['name'],
        "url":event['body-json']['url'],
        "email":event['body-json']['email'],
        "image":event['body-json']['image'],
        "key_info": [
            {
                "public_key":event['body-json']['publicKey'],
                "private_key":event['body-json']['privateKey'],
                "created":str(date.isoformat())
            }
        ],
        "revocations": [],
        "owner":event['body-json']['owner']
    }
    
    issuerProfile = {
        "@context": [
            "https://w3id.org/openbadges/v2",
            "https://w3id.org/blockcerts/v2"
        ],
        "type": "Profile",
        "id": str(newID),
        "name": event['body-json']['name'],
        "url": event['body-json']['url'],
        "introductionURL": str("https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + str(newID) + "/intro"),
        "publicKey": [
            {
                "id": event['body-json']['publicKey'],
                "created": str(date.isoformat())
            }
        ], 
        "revocationList": "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + str(newID) + "/revocations",
        "image": event['body-json']['image'],
        "email": event['body-json']['email']
    }
    
    # update blockcert.issuers
    table.put_item(Item=data)
    
    # create S3 issuer profile
    fileobj = BytesIO(json.dumps(issuerProfile).encode())
    bucket = 'fs.blockcert.poc'
    key = 'issuers/' + str(newID) + '/profile'
    extraArgs = {
        'ACL':'public-read',
        'ContentType':'application/json'
    }
    client.upload_fileobj(fileobj, bucket, key, ExtraArgs=extraArgs)
    
    # update blockcert.users with new owned issuer
    response = tableUsers.scan()
    for i in response['Items']:
        if i['email'] == event['body-json']['owner']:
            ownedIssuers = i['ownedIssuers']
            ownedIssuers.append(str(newID))
            
            ownedIssuers = set(ownedIssuers)
            ownedIssuers = list(ownedIssuers)
            
            tableUsers.update_item(
                Key={
                    'id':i['id']
                },
                UpdateExpression="set ownedIssuers = :ownedIssuers",
                ExpressionAttributeValues={
                    ':ownedIssuers': ownedIssuers
                },
                ReturnValues="UPDATED_NEW"
            )
            break
    
    
    return {
        "id":str(newID)
    }