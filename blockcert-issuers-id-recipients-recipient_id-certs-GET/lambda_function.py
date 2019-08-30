import json
import boto3
import urllib
from io import BytesIO
from boto3.dynamodb.conditions import Key, Attr
import dateutil.parser as parser
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    certList = []
    issuer = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + event['params']['path']['id']
    
    # get recipient information via ID or email
    pID = event['params']['path']['recipient_id']
    response = tableRecipients.scan()
    
    resp_dict = None
    exists = False
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') == pID or resp_dict.get('email') == pID:
            exists = True
            break
    
    # check if recipient exists
    if exists == False:
        raise Exception({
            "errorType": "Exception",
            "httpStatus": 404,
            "message": "Recipient does not exist"
        })
    
    # get certificates awarded to recipient from issuer
    for cert in resp_dict.get('certs'):
        try:
            f = urllib.request.urlopen(cert)
            myfile = f.read()
            d = json.loads(myfile)
            
            if issuer == d['badge']['issuer']['id']:
                data = {
                    "badgeName": d['badge']['name'],
                    "badgeID": d['badge']['id'][9:],
                    "certID": d['id'][9:]
                }
                if data not in certList:
                    certList.append(data)
        except:
            print(1)
    return certList