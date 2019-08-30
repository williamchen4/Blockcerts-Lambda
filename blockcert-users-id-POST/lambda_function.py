import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests

client = boto3.client('cognito-idp')
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

def getIssuerID(issuerName, response):
    resp_dict = 0
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('name') == issuerName:
            return resp_dict.get('id')


def lambda_handler(event, context):

    # user trying to change password
    if 'changePassword' in event['params']['querystring']:
        response = None
        try:
            response = client.change_password(
                PreviousPassword=event['body-json']['oldPassword'],
                ProposedPassword=event['body-json']['newPassword'],
                AccessToken=event['params']['header']['Authorization'][7:]
            )
        except BaseException as e:
            e = str(e)
            errorMessage = 'Invalid New Password'
            if 'NotAuthorizedException' in e:
                errorMessage = 'Incorrect Password'
            elif 'LimitExceededException' in e:
                errorMessage = 'Attempts exceeded. Try again later.'
            raise Exception({
                "errorType" : "Empty",
                "httpStatus": 400,
                "message": errorMessage
            })
        return {"Status":"OK"}
    
    # check authorization
    token = event['params']['header']['Authorization'][7:]
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/authorize/?token=" + token
    headers = {"Authorization":event['params']['header']['Authorization']}
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)

    # mananger is unauthorized
    if 'Manager' in json_data['cognito:groups']:
        raise Exception({
            "errorType" : "Authorization",
            "httpStatus": 401,
            "message": "User is not authorized"
        })
            
    # check if user ID exists
    tableBody = tableUsers.query(KeyConditionExpression=Key('id').eq(event['params']['path']['id']))
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 404,
            "message": "User does not exist"
        })
    

    # if owner call, user status does not change
    if 'Owner' in json_data['cognito:groups']:
        event['body-json']['status'] = tableBody['Items'][0]['status']

    # check empty fields
    for i in event['body-json']:
        if event['body-json'][i] != 'Admin' and len(str(event['body-json'][i])) == 0:
            raise Exception({
                "errorType" : "Empty",
                "httpStatus": 400,
                "message": "Empty Field"
            })
            
    mList = []
    response = tableUsers.scan()
    caller = None
    data = tableBody['Items'][0].copy()

    for user in response['Items']:
        # check if user email already exists
        if user['email'] == event['body-json']['email']:
            if user['id'] != event['params']['path']['id']:
                raise Exception({
                    "errorType" : "Empty",
                    "httpStatus": 409,
                    "message": "This email already has an account"
                })
        # get caller
        if user['email'] == json_data['username']:
            caller = user['id']

    

    # update Cognito if admin status changed
    if tableBody['Items'][0]['admin'] != event['body-json']['admin']:
        oldStatus = tableBody['Items'][0]['admin'][:].capitalize()
        newStatus = event['body-json']['admin'][:].capitalize()
    
        response = client.admin_remove_user_from_group(
            UserPoolId='us-west-2_1UfFbsvl9',
            Username=tableBody['Items'][0]['email'],
            GroupName=oldStatus
        )
        response = client.admin_add_user_to_group(
            UserPoolId='us-west-2_1UfFbsvl9',
            Username=tableBody['Items'][0]['email'],
            GroupName=newStatus
        )
    data['admin'] = event['body-json']['admin']
    
    # update Cognito if enabled/disabled status changed
    if tableBody['Items'][0]['status'] != event['body-json']['status']:
        if event['body-json']['status'] == False:
            response = client.admin_disable_user(
                UserPoolId='us-west-2_1UfFbsvl9',
                Username=tableBody['Items'][0]['email']
            )
        else:
            response = client.admin_enable_user(
                UserPoolId='us-west-2_1UfFbsvl9',
                Username=tableBody['Items'][0]['email']
            )
    data['status'] = event['body-json']['status']

    # update issuers
    response = tableIssuers.scan()

    # changing from owner to manager
    # set previously owned issuers to unowned
    if event['body-json']['admin'] == 'manager' and tableBody['Items'][0]['admin'] == 'owner':
        for issuer in response['Items']:
            if issuer['owner'] == event['body-json']['email']:
                temp = issuer
                temp['owner'] = None
                tableIssuers.put_item(Item=temp)

    
    if 'Admin' in json_data['cognito:groups']:
        # replace managed issuer names with issuer IDs
        data['issuers'] = []
        for issuer in event['body-json']['issuers']:
            issuerID = getIssuerID(issuer, response)
            data['issuers'].append(issuerID)
            
        # update owned issuers
        data['ownedIssuers'] = []
        if event['body-json']['admin'] == 'owner':
            for issuer in event['body-json']['ownedIssuers']:
                issuerID = getIssuerID(issuer, response)
                data['ownedIssuers'].append(issuerID)
    
    else:
        tableCaller = tableUsers.query(KeyConditionExpression=Key('id').eq(caller))
        allOwnedIssuers = set(tableCaller['Items'][0]['ownedIssuers'])
        allManagedIssuers = set(tableBody['Items'][0]['issuers'])
        newIssuers = []
        for issuer in event['body-json']['issuers']:
            newIssuers.append(getIssuerID(issuer, response))
        newIssuers = set(newIssuers)
        data['issuers'] = list((allManagedIssuers.difference(allOwnedIssuers)).union(newIssuers))

    tableUsers.put_item(Item=data)
    
    return {
        "Status":"200 OK"
    }