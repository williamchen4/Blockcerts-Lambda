import boto3
import json
import smtplib
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from io import BytesIO
from botocore.vendored import requests
import pytz
from pytz import timezone


dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')
tableIssuers = dynamodb.Table('blockcert.issuers')
tableBadges = dynamodb.Table('blockcert.badges')
tableInvites = dynamodb.Table('blockcert.invites')

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fs.blockcert.poc')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):

    # Extract parameters
    issuerID = event['params']['path']['id']
    badge_id = event['params']['path']['badge_id']
    recipient_id = event['params']['path']['recipient_id']
    
    # Check if Recipient ID exists
    addresses = []
    recipientEmail = recipient_id
    response = tableRecipients.scan()
    for i in response['Items']:
        if i['email'] == recipient_id:
            recipient_id = i['id']
            addresses = i['addresses']
            break



    # Check if recipient already has address associated with issuer
    recipientAddress = 0
    hasIssuer = False
    #addresses = tableBodyRecipient['Items'][0].get('addresses')
    for i in range(0, len(addresses)):
        if issuerID in addresses[i]:
            hasIssuer = True
            break

    # Send invite if issuer-address pair does not exist
    if hasIssuer == False:
        
        # if unclaimed nonce already exists, add badge to table entry
        response = tableInvites.scan()
        for i in response['Items']:
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if recipientEmail == resp_dict.get('recipient_email') and issuerID == resp_dict.get('issuer_id'):
                x = resp_dict.get('badges')
                if badge_id in x:
                    return "Recipient already has nonce for this badge"
                x.append(badge_id)
                tableInvites.put_item(Item = resp_dict)
                return "New badge added to Invites"
            

        
        return [badge_id]
        
        
        # send new invite to recipient
        #url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/recipients/" + recipient_id + "/invite/" + issuerID
        #badgeList = [badge_id]
        #j = json.dumps(badgeList)
        #return badgeList
        #requests.post(url, data=j).json()
        #return "Invite sent to " + recipient_id
        

    else:
        tableBodyRecipient = tableRecipients.query(KeyConditionExpression=Key('id').eq(recipient_id))
        tableBodyBadge = tableBadges.query(KeyConditionExpression=Key('id').eq(badge_id))
        tableBodyID = tableIssuers.query(KeyConditionExpression=Key('id').eq(issuerID))

        # Get issuer's active public key
        active_public_key = 1
        mList = []
        response = tableIssuers.scan()
        for i in response['Items']:
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('id') == issuerID:
                mList.append(resp_dict.get('key_info'))
    
        for i in mList[0]:
            if "revoked" not in i:
                active_public_key = i["public_key"]
                break

        # Get recipient's address associated with this issuer
        for i in range(0, len(addresses)):
            if issuerID in addresses[i]:
                recipientAddress = addresses[i][issuerID]
                break
    
        # Generate unsigned_cert ID
        unsigned_cert_id = str(uuid.uuid4())
        
        # set pacific time
        date_format='%m/%d/%Y %H:%M:%S %Z'
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))
        
        # get displayHTML info
        data = {
            "issuerID": issuerID, 
            "recipientName":tableBodyRecipient['Items'][0].get('name'),
            "description": tableBodyBadge['Items'][0].get('description'),
            "badgeImage": tableBodyBadge['Items'][0].get('image'),
            "badgeName": tableBodyBadge['Items'][0].get('name'),
            "date": str(date),
            "signature": tableBodyBadge['Items'][0].get('signatureLines')[0]['image'],
            "template": tableBodyBadge['Items'][0].get('template')
        }
        url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/display/"
        header = {"Content-Type":"application/json"}
        response = requests.get(url, headers=header, data = json.dumps(data))
        displayHTML = response.json()

        # Create unsigned_cert
        unsigned_cert = {
            "issuedOn": str(date.isoformat()),
            "recipient": {
                "identity": recipientEmail,
                "type": "email",
                "hashed": False
            },
            "type":"Assertion",
            "verification": {
                "publicKey":"ecdsa-koblitz-pubkey:" + str(active_public_key),
                "type":[
                    "MerkleProofVerification2017",
                    "Extension"
                ]
            },
            "@context":[
                "https://w3id.org/openbadges/v2",
                "https://w3id.org/blockcerts/v2",
                {
                    "displayHtml": { "@id": "schema:description" }
                }  
            ],
            "badge": {
                "issuer": {
                    "url": tableBodyID['Items'][0].get('url'),
                    "name": tableBodyID['Items'][0].get('name'),
                    "email": tableBodyID['Items'][0].get('email'),
                    "type": "Profile",
                    "id": "https://badges.fresnostate.edu/issuers/" + issuerID,
                    "image": tableBodyID['Items'][0].get('image'),
                    "revocationList": "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + issuerID + "/revocations"
                },
                "name": tableBodyBadge['Items'][0].get('name'),
                "type": "BadgeClass",
                "criteria": {
                    "narrative": tableBodyBadge['Items'][0].get('criteria').get('narrative')
                },
                "image": tableBodyBadge['Items'][0].get('image'),
                "id": "urn:uuid:" + badge_id,
                "description": tableBodyBadge['Items'][0].get('description'),
                "signatureLines": tableBodyBadge['Items'][0].get('signatureLines')
            },
            "id": "urn:uuid:" + unsigned_cert_id,
            "recipientProfile": {
                "publicKey": "ecdsa-koblitz-pubkey:" + recipientAddress,
                "name": tableBodyRecipient['Items'][0].get('name'),
                "type":[
                    "RecipientProfile",
                    "Extension"
                ]
            },
            "displayHtml": displayHTML
        }
        
        
        # Upload unsigned certificate to S3
        date = str(date.isoformat())
        s3Date = date[0:4] + date[5:7] + date[8:10] + "/"
        fileobj = BytesIO(json.dumps(unsigned_cert).encode())
        path = 'batch/' + str(s3Date) + str(issuerID) + '/unsigned/' + str(unsigned_cert_id) + ".json"
        bucket.upload_fileobj(fileobj, path, ExtraArgs={'ACL':'public-read'})
        
        
        # Update recipients table with new cert
        tableBody = tableRecipients.query(
        KeyConditionExpression=Key('id').eq(recipient_id)
        )
        path2 = "certs/" + str(unsigned_cert_id) + ".json"
        certLink = "https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/" + path2
        newCerts = tableBody['Items'][0]["certs"] + [certLink]
        data = {
            "addresses":tableBody['Items'][0]['addresses'],
            "certs":newCerts,
            "email":tableBody['Items'][0]["email"],
            "id":tableBody['Items'][0]["id"],
            "name":tableBody['Items'][0]["name"]
        }
        tableRecipients.put_item(Item = data)

        
        return {
            "Status": "200 OK"
        }
        
        