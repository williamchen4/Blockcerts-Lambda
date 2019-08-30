import json
import boto3
import random
import uuid
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableBadge = dynamodb.Table('blockcert.badges')
table2 = dynamodb.Table('blockcert.issuers')

def lambda_handler(event, context):

    issuerID = event['params']['path']['id']
    badgeID = event['params']['path']['badge_id']
    tableBody = tableBadge.query(
    KeyConditionExpression=Key('id').eq(badgeID)
    )
    
    tableBody['Items'][0]['template'] = event['body-json']['template']
    tableBadge.put_item(Item=tableBody['Items'][0])