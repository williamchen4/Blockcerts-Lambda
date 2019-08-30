import json
from datetime import date

import boto3
client = boto3.client('s3')

def writeToJSON(issuer, fileName, data):
    pathName = '/tmp/' + fileName + '.json'
    with open(pathName, 'w') as fp:
        json.dump(data, fp)

def lambda_handler(event, context):
    writeToJSON(event['issuer'], event['certificate'])
    
    bucketName = 'fs.blockcerts.poc'
    todayFolder=str(date.today()).replace("-","")
    
    result = client.list_objects(Bucket=bucketName, Prefix="batch/"+todayFolder)
    if result:
        print (result)
        # print("Folder %s exists!" %(todayFolder))
    else:
        print("Folder %s does not exist!" %(todayFolder))
        
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }