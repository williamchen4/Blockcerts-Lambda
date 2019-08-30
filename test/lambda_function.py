import json
import sys
import glob
import boto3
from pprint import pprint
from botocore.exceptions import ClientError
from botocore.vendored import requests

AWS_REGION = ""
CHARSET = "UTF-8"
SENDER = ""
RECIPIENT = ""
SUBJECT = "Here is your Fresno State Blockcerts Certificate"

FILE_NAME = ""
FILE_ID = ""

BODY_TEXT = ("Open to claim your Blockcerts certificate!\r\n")

# Removes the prefix from the cert path to get only cert
def remove_prefix(text):
    if text.startswith('/var/blockcerts/blockchain_certificates/'):
        return text[len('/var/blockcerts/blockchain_certificates/'):]
    return text

# Removes the prefix before the cert id
def remove_id_prefix(text):
    if text.startswith('urn:uuid:'):
        return text[len('urn:uuid:'):]
    return text

def lambda_handler(argv,v):
    if(len(argv) < 2):
        print('Region not found. use `python email_recipients.py $region`')
        exit()

    global AWS_REGION
    AWS_REGION = argv[3].strip('\"')

    payload = []
    for file in glob.glob("/var/blockcerts/blockchain_certificates/*.json"):
        with open(file) as json_data:
            data = json.load(json_data)
            payload.append({
                'recipientEmail': data['recipient']['identity'],
                'recipientName': data['recipientProfile']['name'].split()[0],
                'fileID': data['id'][9:]
            })
    url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/award-email"
    requests.post(url, json=payload)

if __name__ == '__main__':
    main(sys.argv)