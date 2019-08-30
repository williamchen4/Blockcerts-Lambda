import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableUsers = dynamodb.Table('blockcert.users')
tableIssuers = dynamodb.Table('blockcert.issuers')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
        
def lambda_handler(event, context):
    
    # returns user information
    # search by ID or email
    
    # check admin status
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)

    if 'Manager' in json_data['cognito:groups']:
        raise Exception({
            "errorType" : "Unauthorized",
            "httpStatus": 401,
        })
    
    # search by ID or email
    idOrEmail = event['params']['path']['id']
    resp = []
    response = tableUsers.scan()
    caller = []
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('id') == idOrEmail or resp_dict.get('email') == idOrEmail:
            resp = resp_dict
        if resp_dict.get('email') == json_data['username']:
            caller = resp_dict
        if resp != [] and caller != []:
            break

    # user does not exist
    if resp == []:    
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "User does not exist"
        })
    elif resp.get('admin') != 'manager' and caller.get('admin') == 'owner':
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "Unauthorized"
        })

    managedIssuerIDs = resp.get('issuers')
    ownedIssuerIDs = resp.get('ownedIssuers')
    managedIssuers = []
    ownedIssuers = []
    nonManagedIssuers = []
    nonOwnedIssuers = []
    

    if 'Owner' in json_data['cognito:groups']:
        managedIssuerIDs = list(set(managedIssuerIDs).intersection(set(caller.get('ownedIssuers'))))
    

    # get managed and owned issuer names
    response = tableIssuers.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        
        if 'Owner' in json_data['cognito:groups']:
            if resp_dict.get('id') in managedIssuerIDs:
                managedIssuers.append(resp_dict.get('name'))
            elif resp_dict.get('id') in caller.get('ownedIssuers'):
                nonManagedIssuers.append(resp_dict.get('name'))
            
        # admin call
        else:
            if resp_dict.get('id') in managedIssuerIDs:
                managedIssuers.append(resp_dict.get('name'))
                #mList.append({"id": resp_dict.get('id'), "name": resp_dict.get('name')})
            elif resp_dict.get('id') not in ownedIssuerIDs:
                nonManagedIssuers.append(resp_dict.get('name'))
            if resp_dict.get('id') in ownedIssuerIDs:
                ownedIssuers.append(resp_dict.get('name'))
            else:
                nonOwnedIssuers.append(resp_dict.get('name'))
                
    resp['issuers'] = managedIssuers
    resp['ownedIssuers'] = ownedIssuers
    resp['nonManagedIssuers'] = nonManagedIssuers
    resp['nonOwnedIssuers'] = nonOwnedIssuers
    
    return resp