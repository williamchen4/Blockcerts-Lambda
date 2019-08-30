import json
import boto3
from datetime import datetime
import urllib
from botocore.vendored import requests
import base64

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fs.blockcert.poc')

def lambda_handler(event, context):
    
    # get certificate information
    searchKey = "certs/" +  event['params']['path']['id']
    link = "https://s3-us-west-2.amazonaws.com/fs.blockcerts.poc/batch/20181205/1/unsigned/cd316fa9-5301-424c-9d87-867abc22c647.json"
    for a in bucket.objects.all():
        if searchKey in str(a):
            link = "https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/" + str(a.key)
            break
    if link == 1:
        return 'error'
    else:
        f = urllib.request.urlopen(link)
        myfile = f.read()
        cert = json.loads(myfile)


        # return json
        if "format" not in event['params']['querystring']:
            return cert
        # return badge image
        elif event['params']['querystring']['format'] == 'badge':
            base64 = cert['badge']['image']
            
            
            if base64[-1].isalpha() == False:
                return base64[:-2]
            else:
                return base64
        elif event['params']['querystring']['format'] == 'html':
            return cert['displayHtml']
