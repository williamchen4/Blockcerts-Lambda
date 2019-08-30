import json
from datetime import datetime
from datetime import date
import boto3
from boto3.dynamodb.conditions import Key, Attr
import pytz
from pytz import timezone
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

    username = json_data.get('username')
    
    # set pacific time
    date_format='%m/%d/%Y %H:%M:%S %Z'
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    
    lastLogout = str(date.isoformat())
    response = table.scan()
    for i in response['Items']:
        if username == i['email']:
            i['lastLogout'] = lastLogout
            table.put_item(Item = i)
            return {"Status":"200"}

    raise Exception({
        "errorType" : "Exception",
        "httpStatus": 400
    })
    