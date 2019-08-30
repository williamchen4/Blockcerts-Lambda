import json
import boto3
from botocore.vendored import requests

def lambda_handler(event, context):
    
    # exchange code for access token and refresh token
    code = event['params']['querystring']['code']
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    data = {
        'grant_type':'authorization_code',
        'client_id':'2qoad5283o8vbn15mnr99oa0v1',
        'client_secret': '1sfddc1pki9no8b7d626kijpvlrmkeuknem0v3uf96umlnt70cop',
        'code':code,
        'redirect_uri':'https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/redirect'
    }

    url = "https://blockcerts.auth.us-west-2.amazoncognito.com/oauth2/token"
    response = requests.post(url, headers=headers, data=data)
    json_data = json.loads(response.text)
    urlEnd = "access_token=" + json_data['access_token'] + "&refresh_token=" + json_data['refresh_token']


    #return urlEnd
    #return {"location":"http://localhost:4200?" + urlEnd}
    return {"location":"http://fs.blockcert.poc.web.s3-website-us-west-2.amazonaws.com/?" + urlEnd}
    
    #return {"location":"http://fswillc1.s3-website-us-west-2.amazonaws.com/?" + urlEnd}
