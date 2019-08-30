import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRevocations = dynamodb.Table('blockcert.revocations')
tableIssuers = dynamodb.Table('blockcert.issuers')

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fs.blockcert.poc')

def lambda_handler(event, context):
    
    # check if issuer ID exists
    issuerID = event['params']['id']
    tableBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(issuerID)
    )
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "Issuer does not exist"
         })    
    
    # check if cert ID exists
    certExists = False
    searchKey = "certs/" +  event['params']['uuid'] + ".json"
    for a in bucket.objects.all():
        if searchKey in str(a):
            certExists = True
            break
    if certExists == False:
        raise Exception({
            "errorType": "Exception",
            "httpStatus": 404,
            "message": "Certificate ID does not exist"
        })
        
    # check if certificate already revoked
    tableRevocationsBody = tableRevocations.query(
    KeyConditionExpression=Key('id').eq(event['params']['uuid'])
    )
    if tableRevocationsBody['Count'] != 0:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "Certificate already revoked"
         }) 
         
    data = {
        "id": event['params']['uuid'],
        "issuer_id": issuerID,
        #"cert_id": event['params']['uuid'],
        "reason": event['body']['revocationReason']
    }
    
    # update blockcert.revocations
    tableRevocations.put_item(Item = data)
    
    # update blockcert.issuers
    mList = tableBody['Items'][0].get('revocations')
    mList.append({"cert_id":event['params']['uuid'], "reason":event['body']['revocationReason']})
    data = {
        "id":issuerID,
        "email":tableBody['Items'][0].get('email'),
        "image":tableBody['Items'][0].get('image'),
        "key_info":tableBody['Items'][0].get('key_info'),
        "name":tableBody['Items'][0].get('name'),
        "url":tableBody['Items'][0].get('url'),
        "revocations":mList
    }
    tableIssuers.put_item(Item = data)
    return {
        "Status":"200 OK"
    }