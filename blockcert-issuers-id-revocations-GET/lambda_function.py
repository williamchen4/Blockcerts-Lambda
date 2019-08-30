import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.revocations')
tableIssuers = dynamodb.Table('blockcert.issuers')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    
    # Check if Issuer ID exists
    issuerID = event['params']['id']
    tableBody = tableIssuers.query(
    KeyConditionExpression=Key('id').eq(issuerID)
    )
    if tableBody['Count'] == 0:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Issuer ID does not exist"
        })
    

    mList = []
    response = table.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('issuer_id') == issuerID:
            data = {
                "id": "urn:uuid:" + resp_dict.get('id'),
                "revocationReason":resp_dict.get('reason')
            }
            mList.append(data)
    

    data = {
        "@context": "https://w3id.org/openbadges/v2",
        "id": "http://blockcerts.fresnostate.edu/issuers/" + issuerID + "/revocations",
        "type": "RevocationList",
        "issuer": "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + issuerID,
        "revokedAssertions": mList
    }
    
    return data