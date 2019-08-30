import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.badges')
tableID = dynamodb.Table('blockcert.issuers')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    
    # check if issuer ID exists
    pID = event['params']['id']
    tableIDBody = tableID.query(
    KeyConditionExpression=Key('id').eq(pID)
    )
    if tableIDBody['Count'] == 0:
        raise Exception({
            "errorType":"Exception",
            "httpStatus":404,
            "message":"Issuer does not exist"
        })

    # get all badge IDs associated with issuer ID
    mList = []
    response = table.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('issuer_id') == pID:
            mList.append({"id":resp_dict.get('id'), "name":resp_dict.get('name')})
            
    return sorted(mList, key=lambda k: k['name'])

    