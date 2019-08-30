import json
import boto3
import urllib
from io import BytesIO
from botocore.client import Config
from boto3.dynamodb.conditions import Key, Attr
import dateutil.parser as parser
from botocore.vendored import requests
import zipfile
import os

client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')
tableIssuers = dynamodb.Table('blockcert.issuers')
tableUsers = dynamodb.Table('blockcert.users')
tableBadges = dynamodb.Table('blockcert.badges')

def lambda_handler(event, context):

    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    
    username = json_data['username']
    isAdmin = 'Admin' in json_data['cognito:groups']
    
    exportedIssuers = []
    
    # create zip
    bucket = 'fs.blockcert.poc'
    
    zip_buffer = BytesIO()
    zf = zipfile.ZipFile(zip_buffer, 'w')
    
    # add certs to zip
    certKeys = client.list_objects_v2(Bucket=bucket, Prefix='certs')
    for obj in certKeys['Contents'][1:]:
        response = client.get_object(Bucket=bucket, Key=obj['Key'])
        zf.writestr(obj['Key'], response['Body'].read())
        
    # add recipients to zip
    tableRecipientsBody = tableRecipients.scan()
    for item in tableRecipientsBody['Items']:
        zf.writestr('recipients/' + item['id'] + '.json', json.dumps(item))

    # add users to zip
    tableUsersBody = tableUsers.scan()
    for item in tableUsersBody['Items']:
        zf.writestr('users/' + item['id'] + '.json', json.dumps(item))
        if item['email'] == username and not isAdmin:
            exportedIssuers = item['ownedIssuers']

    # add issuers to zip
    tableBadgesBody = tableBadges.scan()
    issuerKeys = client.list_objects_v2(Bucket=bucket, Prefix='issuers')
    for obj in issuerKeys['Contents'][1:]:
        issuerID = obj['Key'][8:-8]
        if len(issuerID) > 0:
            if isAdmin or issuerID in exportedIssuers:
                # profile
                response = client.get_object(Bucket=bucket, Key=obj['Key']) 
                zf.writestr(obj['Key'] + '.json', response['Body'].read())  
                # badges
                for item in tableBadgesBody['Items']:                      
                    if item['issuer_id'] == issuerID:
                        zf.writestr('issuers/' + issuerID + '/badges/' + item['id'] + '.json', json.dumps(item))
                # revocations       
                try:                                                        
                    url = 'https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/' + issuerID + '/revocations'
                    zf.writestr('issuers/' + issuerID + '/revocations.json', requests.get(url).text)
                except:
                    pass
        

    zf.close()
    zip_buffer.seek(0)
    client.upload_fileobj(zip_buffer, bucket, 'exports/uBadges-' + username[:username.index('@')] + '.zip')
    
    
    # return download link
    key = 'exports/uBadges-' + username[:username.index('@')] + '.zip'
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'fs.blockcert.poc',
            'Key': key,
            'ResponseContentDisposition': 'attachment'
        }
    )

    return url
    