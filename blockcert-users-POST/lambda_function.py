import json
import boto3
import random
import hashlib
from datetime import datetime
from botocore.vendored import requests

from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr

client = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.users')
    
def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature
    hash_string = 'confidential data'
    sha_signature = encrypt_string(hash_string)
    return sha_signature

def lambda_handler(event, context):
    
    # check authorization
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)

    if 'Manager' in json_data['cognito:groups']:
        raise Exception({
            "errorType" : "Authorization",
            "httpStatus": 401,
            "message": "User is not authorized"
        })

    if 'Owner' in json_data['cognito:groups']:
        event['body-json']['admin'] = 'manager'
        
    # check empty fields
    for i in event['body-json']:
        if event['body-json'][i] != 'Admin' and len(str(event['body-json'][i])) == 0:
            raise Exception({
                "errorType" : "Empty",
                "httpStatus": 400,
                "message": "Empty Field"
            })
    
    # get previous largest ID
    mList = []
    eList = []
    response = table.scan()
    for i in response['Items']: 
        mList.append(i['id'])
        eList.append(i['email'])

        # check if existing user email
        if event['body-json']['email'] in eList:
            raise Exception({
                    "errorType" : "Empty",
                    "httpStatus": 409,
                    "message": "This email already has an account"
            })

    prevID = 0
    for i in mList:
        if prevID < int(i):
            prevID = int(i)
    newID = prevID + 1
    event['body-json']['id'] = str(newID)
    ########################################

    # update Cognito
    groupName = event['body-json']['admin'].capitalize()
    
    response = client.admin_create_user(
        UserPoolId='us-west-2_1UfFbsvl9',
        Username=event['body-json']['email'],
        UserAttributes=[
            {
                "Name": "email",
                "Value": event['body-json']['email']
            },
            {
                'Name': 'email_verified',
                'Value': 'true'
            }
         ],
        ForceAliasCreation=True,
        DesiredDeliveryMediums=['EMAIL']
    )
    response = client.admin_add_user_to_group(
        UserPoolId = 'us-west-2_1UfFbsvl9',
        Username = event['body-json']['email'],
        GroupName = groupName
    )    

    
    # update blockcert.users table
    data = {
        "id":str(newID),
        "email":event['body-json']['email'],
        "admin":event['body-json']['admin'],
        "issuers":[],
        "status":True,
        "ownedIssuers":[]
    }
    table.put_item(Item=data)
    
    return {
        "Status":"200 OK"
    }
    
    
