import urllib.request
import json
import time
from jose import jwk, jwt
from jose.utils import base64url_decode


keys_url = 'https://cognito-idp.us-west-2.amazonaws.com/us-west-2_1UfFbsvl9/.well-known/jwks.json'

response = urllib.request.urlopen(keys_url)
keys = json.loads(response.read())['keys']

def lambda_handler(event, context):
    token = event['params']['header']['Authorization'][7:]
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return 'abc'
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return 'def'
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return 'ggg'
    # and the Audience  (use claims['client_id'] if verifying an access token)
    #if claims['aud'] != app_client_id:
        #print('Token was not issued for this audience')
        #return 'hhh'
    # now we can use the claims

    isAdmin = "Admin" in claims['cognito:groups']
    return {
        "username":claims['username'],
        "isAdmin":isAdmin,
        "userType":claims['cognito:groups'][0]
    }
        
# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token': ''}
    lambda_handler(event, None)