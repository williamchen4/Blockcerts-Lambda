import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.users')

def lambda_handler(event, context):

    # check admin status
    token = event['headers']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/login/?token=" + token
    response = requests.post(url, params = {'Admin':True})
    json_data = json.loads(response.text)

    if json_data == False:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 401,
        })
    
    
    issuerID = event['params']['id']
    revokedUsers = event['body']['unallowedUsers']
    addedUsers = event['body']['allowedUsers']
    
    # Revoke users
    for revokedUser in revokedUsers:
        tableBody = table.query(
        KeyConditionExpression=Key('id').eq(revokedUser)
        )
        
        updatedIssuers = []
        for i in tableBody['Items'][0]['issuers']:
            if i != issuerID:
                updatedIssuers.append(i)
        data = {
            "id":tableBody['Items'][0]['id'],
            "admin":tableBody['Items'][0]['admin'],
            "email":tableBody['Items'][0]['email'],
            "issuers":updatedIssuers
        }
        table.put_item(Item = data)
        
    # Add users
    for addedUser in addedUsers:
        tableBody = table.query(
        KeyConditionExpression=Key('id').eq(addedUser)
        )
        if issuerID not in tableBody['Items'][0]['issuers']:
            data = {
                "id":tableBody['Items'][0]['id'],
                "admin":tableBody['Items'][0]['admin'],
                "email":tableBody['Items'][0]['email'],
                "issuers":tableBody['Items'][0]['issuers'] + [issuerID]
            }
            table.put_item(Item = data)
    