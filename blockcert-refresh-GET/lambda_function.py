import json
import boto3
client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    
    # takes in a refresh token and returns an access token
    
    refreshToken = event['params']['header']['Authorization'][7:]
    response = client.admin_initiate_auth(
        UserPoolId='us-west-2_1UfFbsvl9',
        ClientId='2qoad5283o8vbn15mnr99oa0v1',
        AuthFlow='REFRESH_TOKEN',
        AuthParameters={
            'REFRESH_TOKEN':refreshToken,
            'SECRET_HASH':'1sfddc1pki9no8b7d626kijpvlrmkeuknem0v3uf96umlnt70cop'
        }
    )
    return response['AuthenticationResult']['AccessToken']