import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

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

    '''
    # return unowned issuers
    if 'Admin' in json_data['cognito:groups'] and "unowned" in event['params']['querystring']:
        ownedIssuers = []
        allIssuerIDs = []        
        allUsers = tableUsers.scan()
        for issuer in allUsers['Items']:
            ownedIssuers.append(issuer['ownedIssuers'])
        ownedIssuers = [item for sublist in ownedIssuers for item in sublist]
        allIssuers = tableIssuers.scan()
        for issuer in allIssuers['Items']:
            allIssuerIDs.append(issuer['id'])
        unownedIssuers = [issuer for issuer in allIssuerIDs if issuer not in ownedIssuers]
        unownedIssuersNamed = []
        for issuer in allIssuers['Items']:
            if issuer['id'] in unownedIssuers:
                unownedIssuersNamed.append({"id":issuer['id'], "name":issuer['name']})
        return sorted(unownedIssuersNamed, key=lambda k: k['name'])        
    '''
    
    # return owned issuers
    if 'Owner' in json_data['cognito:groups'] and 'owner' in event['params']['querystring']:
        username = json_data['username']
        issuerList = []
        response = tableUsers.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('email') == username:
                issuerList = resp_dict.get('ownedIssuers')
                break
        mList = []
        response = tableIssuers.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('id') in issuerList:
                mList.append({"id":resp_dict.get('id'), "name":resp_dict.get('name'), "image":resp_dict.get('image')})
        return sorted(mList, key=lambda k: k['name'])
    
    # if manager or owner looking for issuers, not owned issuers
    elif "Manager" in json_data['cognito:groups'] or "Owner" in json_data['cognito:groups']:
        username = json_data['username']
        issuerList = []
        response = tableUsers.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('email') == username:
                issuerList = resp_dict.get('issuers')
                issuerList.append(resp_dict.get('ownedIssuers'))
                issuerList = [item for sublist in issuerList for item in sublist]
                break
        mList = []
        response = tableIssuers.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            if resp_dict.get('id') in issuerList:
                mList.append({"id":resp_dict.get('id'), "name":resp_dict.get('name'), "image":resp_dict.get('image')})
        return sorted(mList, key=lambda k: k['name'])
        
    # admin access; return list of all issuers
    else:
        mList = []
        response = tableIssuers.scan()
        for i in response['Items']: 
            json_str = json.dumps(i, cls=DecimalEncoder)
            resp_dict = json.loads(json_str)
            mList.append({"id":resp_dict.get('id'), "name":resp_dict.get('name'), "image":resp_dict.get('image')})
            
        return sorted(mList, key=lambda k: k['name'])