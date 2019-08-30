import json
import boto3
import urllib
from botocore.vendored import requests
import base64

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fs.blockcert.poc')

def lambda_handler(event, context):
    
    # search for cert with corresponding ID
    searchKey = "certs/" +  event['pathParameters']['id']
    link = 1
    for a in bucket.objects.all():
        if searchKey in str(a):
            link = "https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/" + str(a.key)
            break
    
    # get badge image from cert
    f = urllib.request.urlopen(link)
    myfile = f.read()
    cert = json.loads(myfile)
    base64 = cert['badge']['image'][22:]
    
    return({
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
                "content-type": "image/png",
        },  
        'body':base64
    })

    
    