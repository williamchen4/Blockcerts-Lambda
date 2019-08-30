import json
import boto3
from datetime import datetime
from datetime import date
from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr
import dateutil.parser as parser
from botocore.vendored import requests
import pytz
from pytz import timezone

client = boto3.client('s3')
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

    # check admin status
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    
    # check not manager
    if 'Manager' in json_data['cognito:groups']:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 401
        })
        
    # if owner, check if have access to this issuer
    elif 'Owner' in json_data['cognito:groups']:
        response = tableUsers.scan()
        for i in response['Items']:
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('email') == json_data['username']:
                if event['params']['path']['id'] not in resp_dict.get('ownedIssuers'):
                    raise Exception({
                        "errorType" : "Authorization",
                        "httpStatus": 401,
                        "message":"Owner does not have access to this issuer"
                    })

    # Check if Issuer ID exists
    pID = event['params']['path']['id']
    tableBody = tableIssuers.query(KeyConditionExpression=Key('id').eq(pID))
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "Issuer does not exist"
            })
    
    # if called by owner, cannot change owner        
    if 'Owner' in json_data['cognito:groups']:
        event['body-json']['owner'] = tableBody['Items'][0]['owner']
    # check empty image
    if event['body-json']['image'] == None:
        event['body-json']['image'] = tableBody['Items'][0]['image']
        
    # check empty fields
    for i in event['body-json']:
        if i != 'owner':
            if len(event['body-json'][i]) == 0:
                raise Exception({
                    "errorType" : "Empty",
                    "httpStatus": 400,
                    "message": "Empty Field"
                 }) 
             
    response = tableIssuers.scan()
    # check existing name
    if event['body-json']['name'] != tableBody['Items'][0]['name']:
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('name') == event['body-json']['name']:
                raise Exception({
                    "errorType" : "Conflict",
                    "httpStatus": 409,
                    "message": "Issuer name already exists"
                })
            
    # Revoke previous active key
    mList = []
    revocations = []
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') == pID:
            mList.append(resp_dict.get('key_info'))
            revocations=resp_dict.get('revocations')
    

    newPublicKey = True
    for i in mList[0]:
        if i['public_key'] == event['body-json']['publicKey']:
            newPublicKey = False
            break
        
    # set pacific time
    #date_format='%m/%d/%Y %H:%M:%S %Z'
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    
    if newPublicKey == True:

        # Revoke old key
        for i in mList[0]:
            if "revoked" not in i:
                i["revoked"] = str(date.isoformat())
                #i["revoked"] = str(datetime.now())
                
        # Set new active key
        mList[0].append({
            "public_key":event['body-json']['publicKey'],
            "private_key":event['body-json']['privateKey'],
            "created":str(date.isoformat())
        })
    
    # create data for blockcert.issuers
    data = {
        "id":pID,
        "name":event['body-json']['name'],
        "url":event['body-json']['url'],
        "email":event['body-json']['email'],
        "image":event['body-json']['image'],
        "key_info":mList[0],
        "revocations":revocations,
        "owner": event['body-json']['owner']
    }
    
    tableIssuers.put_item(Item=data)
    
    # update issuer profile in S3
    bucket = 'fs.blockcert.poc'
    key = 'issuers/' + str(pID) + '/profile'
    response = client.get_object(Bucket=bucket, Key=key)
    issuerProfile = json.loads(response['Body'].read().decode('utf-8'))
    
    issuerProfile['name'] = data['name']
    issuerProfile['url'] = data['url']
    issuerProfile['email'] = data['email']
    issuerProfile['image'] = data['image']
    issuerProfile['publicKey'] = [{
            "id": event['body-json']['publicKey'],
            "created":data['key_info'][-1]['created']
        }]
        
    fileobj = BytesIO(json.dumps(issuerProfile).encode())
    extraArgs = {
        'ACL':'public-read',
        'ContentType':'application/json'
    }
    client.upload_fileobj(fileobj, bucket, key, ExtraArgs=extraArgs)
    
    
    
    # update blockcert.users
    ownedIssuers=[]
    response = tableUsers.scan()
    userID = None
    for i in response['Items']:
        if i['email'] == event['body-json']['owner']:
            userID = i['id']
            ownedIssuers = i['ownedIssuers']
            if pID not in ownedIssuers:
                ownedIssuers.append(pID)
        # remove old owner
        if pID in i['ownedIssuers'] and i['id'] != userID:
            i['ownedIssuers'].remove(pID)
            response = tableUsers.update_item(
                Key={
                    'id':i['id']
                },
                UpdateExpression="set ownedIssuers = :x",
                ExpressionAttributeValues={
                    ':x': i['ownedIssuers']
                },
                ReturnValues="UPDATED_NEW"
            )
    # set new owner
    if userID != None:
        response = tableUsers.update_item(
            Key={
                'id':userID
            },
            UpdateExpression="set ownedIssuers = :x",
            ExpressionAttributeValues={
                ':x': ownedIssuers
            },
            ReturnValues="UPDATED_NEW"
        )
    
    return {
        "id":pID
    }