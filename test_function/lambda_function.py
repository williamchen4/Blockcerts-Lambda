import json
import boto3
import random
import hashlib
from datetime import datetime
from botocore.vendored import requests

from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('test')
    
def lambda_handler(event, context):

    data = {
        "id":str(event['status'])
    }
    table.put_item(Item=data) 
