import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableIssuers = dynamodb.Table('blockcert.issuers')
tableBadges = dynamodb.Table('blockcert.badges')

def lambda_handler(event, context):
    pID = event['params']['id']
    badgeID = event['params']['badge_id']

    # check if issuer exists
    tableIssuersBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(pID)
    )
    if tableIssuersBody['Count'] == 0:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Issuer does not exist"
        })    
    
    # check if badge exists
    tableBadgeBody = tableBadges.query(
    KeyConditionExpression=Key('id').eq(badgeID)
    )
    if tableBadgeBody['Count'] == 0 or tableBadgeBody['Items'][0]['issuer_id'] != pID:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Badge does not exist"
        })    
    issuerInfo = tableIssuersBody['Items'][0]
    badgeInfo = tableBadgeBody['Items'][0]
    
    # set signature type
    signatures = badgeInfo.get('signatureLines')
    for i in signatures:
        i['type'] = ["SignatureLine", "Extension"]

    # return data
    data = {
        "signatureLines":signatures,
        "id":badgeID,
        "issuer": {
            "revocationList":"---------------placeholder---------------",
            "email":issuerInfo.get('email'),
            "type":"Profile",
            "id":issuerInfo.get('id'),
            "url":issuerInfo.get('url'),
            "image":issuerInfo.get('image'),
            "name":issuerInfo.get('name')
        },
        "type":"BadgeClass",
        "image":badgeInfo.get('image'),
        "criteria": {
            "narrative": badgeInfo.get('criteria').get('narrative')
        },
        "name":badgeInfo.get('name'),
        "description":badgeInfo.get('description')
    }
    
    return data