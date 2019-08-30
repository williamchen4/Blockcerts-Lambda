import boto3
from botocore.client import Config

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

def lambda_handler(event, context):
    
    # link to download certificate
    
    key = 'certs/' + str(event['params']['path']['id']) + '.json'
    
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'fs.blockcert.poc',
            'Key': key,
            'ResponseContentDisposition': 'attachment'
        }
    )

    return {"location":url}

