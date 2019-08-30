import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.users')

def lambda_handler(event, context):
    
    # check admin status
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    
    if 'Manager' in json_data['cognito:groups']:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 401,
        })
    
    isSettingOwner = False
    if 'owner' in event['params']['querystring']:
        isSettingOwner = True
     
    # return users   
    idList = []
    emailList = []
    ownerList = []
    
    response = table.scan()
    for i in response['Items']:
        if isSettingOwner and i['admin'] == 'owner':
            ownerList.append({'id': i['id'], 'email': i['email']})
        else:
            idList.append(i['id'])
            emailList.append(i['email'])

    if isSettingOwner:
        return sorted(ownerList, key = lambda k: k['email'])
    else:
        return ({"id":idList, 'email':emailList})