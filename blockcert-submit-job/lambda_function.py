import json
from datetime import date
import boto3

BATCH = boto3.client('batch')

# Submits Batch job with input to function
# example input:
#
# {
#  "batch": "s3://fs.blockcerts.poc/batch/20181213/",
#  "certs": "s3://fs.blockcerts.poc/certs/"
# }
#

def lambda_handler(event, context):

    batchFolder = event['batch']
    certsFolder = event['certs']
    today = str(date.today()).replace("-","") # Creates string with today's date 

    BATCH.submit_job(
        jobName="batch_"+today,
        jobQueue='arn:aws:batch:us-west-2:010063476047:job-queue/blockcerts-issuer-queue',
        jobDefinition='arn:aws:batch:us-west-2:010063476047:job-definition/blockcerts-issuer:5',
        containerOverrides={
            'vcpus': 2,
            'memory': 2000,
            'command': [
                str(batchFolder),
                str(certsFolder),
                ],
        }
    )
    
    return {
        'statusCode': 200,
    }