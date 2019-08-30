import json
import boto3
from datetime import datetime
import urllib
from botocore.vendored import requests

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fs.blockcert.poc')


def lambda_handler(event, context):

    # get certificate information
    searchKey = "certs/" +  event['params']['path']['id']
    link = None
    for a in bucket.objects.all():
        if searchKey in str(a):
            link = "https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/" + str(a.key)
            break
     
    # nonexistant certificate ID  
    if link == None:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Certificate does not exist"
        })
    
    # return certificate HTML
    else:
        f = urllib.request.urlopen(link)
        myfile = f.read()
        cert = json.loads(myfile)
        return cert['displayHtml']