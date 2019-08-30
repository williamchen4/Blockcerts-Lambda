import boto3
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.issuers')

def lambda_handler(event, context):
    
    pID = event['params']['path']['id']
    tableBody = table.query(
    KeyConditionExpression=Key('id').eq(pID)
    )
    return tableBody['Items'][0]['image']
    
    '''
    # get certificate information
    #searchKey = "certs/" +  event['params']['path']['id']
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": json.dumps({
            "1":
        })
    }
    link = "https://s3-us-west-2.amazonaws.com/fs.blockcerts.poc/batch/20181205/1/unsigned/cd316fa9-5301-424c-9d87-867abc22c647.json"
    for a in bucket.objects.all():
        if searchKey in str(a):
            link = "https://s3-us-west-2.amazonaws.com/fs.blockcerts.poc/" + str(a.key)
            break

    if link == 1:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {},
            "body": json.dumps({
                "greeting": "Hello John"
            })
        }    
    else:
    
        f = urllib.request.urlopen(link)
        myfile = f.read()
        cert = json.loads(myfile)

        base64 = cert['badge']['image']
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {},
            "body": json.dumps({
                "greeting": "Hello John"
            })
        }
    '''