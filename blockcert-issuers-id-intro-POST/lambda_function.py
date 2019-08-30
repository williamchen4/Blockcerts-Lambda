import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from io import BytesIO
from botocore.vendored import requests

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')
tableIssuers = dynamodb.Table('blockcert.issuers')
tableBadges = dynamodb.Table('blockcert.badges')
tableInvites = dynamodb.Table('blockcert.invites')
test = dynamodb.Table('test')

s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fs.blockcert.poc')
tableInvites = dynamodb.Table('blockcert.invites')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
        
def lambda_handler(event, context):
    # check if valid nonce
    tableBody = tableInvites.query(
    KeyConditionExpression=Key('id').eq(event['body']['nonce'])
    )
    
    # nonce does not exist
    if tableBody['Count'] == 0 or tableBody['Items'][0]['issuer_id'] != event['params']['id']:
        raise Exception({
            "errorType" : "Exception",
            "httpStatus": 400,
            "message": "Invalid code"
        })
    #if tableBody['Items'][0]['issuer_id'] != 
    # get parameters
    recipientEmail = tableBody['Items'][0]["recipient_email"]
    issuerID = tableBody['Items'][0]["issuer_id"]
    badges = tableBody['Items'][0]["badges"]
    recipientAddress = event['body']['bitcoinAddress']
    
    # remove entry in blockcert.invites
    tableInvites.delete_item(Key={"id":event['body']['nonce']})
    recipientID=None
    # Add issuer-address pair to recipients table
    xList = []
    response = tableRecipients.scan()
    for i in response['Items']:
        json_str = json.dumps(i, cls=DecimalEncoder)
        resp_dict = json.loads(json_str)
        if resp_dict.get('email') == recipientEmail:
            xList.append(resp_dict.get('addresses'))
            recipientID = resp_dict.get('id')
    
    xList[0].append({issuerID:recipientAddress})
    
    tableBody = tableRecipients.query(
    KeyConditionExpression=Key('id').eq(recipientID)
    )
    
    data = {
        "addresses":xList[0],
        "certs":tableBody['Items'][0]["certs"],
        "email":tableBody['Items'][0]["email"],
        "id":tableBody['Items'][0]["id"],
        "name":tableBody['Items'][0]["name"]
    }
    tableRecipients.put_item(Item=data)
    
    
    # Issue all badges now that recipient has an address associated with issuer
    refreshToken="Bearer eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.O20xoYZxZk0Rjxh8q5axg1PPRHU86zu5hjpnbGpnqKBAjaOnqEJmaYJ1E37ucPBkEasF_WFZ5BAFmt_qLOQvl3AbsSLqQs_QAc0aS5nXJX90ujbUrBFQcmMlOyhZzt9rv8_u-WuKIhO-wYk1JLf8Piznzl7m2ML_BVWNs558-QQoyxBU1HopNouPoK-WNWT-xR73I310KdmGD_28zJ0bRRRJuC0EH0sR3UATMIeiWkVfC3p6IIOwXbBOb3nbS-55KL8u4kokiisybozJVu0e1vT401nwn598zpwGtKGR8RO3RzKhlsEFx11Lfy8vqGqBTu0dWOHFz7snCeEwcAkzJQ.FGmkfRJCsyz5WhJ0.CG0VvasU_cjOtJaxwjPYteEhO1_ST3tMOdevLED3qKo8SpA7iGFSvDrJumYaW6pNZd5o1do99qqPNMr406K_nuTCtKIkzQygxnPkozLIsCsBVqB6Y7In9ba_4Nwy9z29zc4Bt-P58oZrLYMr4UnD47fu_zhKtHyM3UbENoq5lS_bsC3Ja9unKlnzymlv65OMiYF9hHH0G_kkZuypzdE_wt3_7GRFYw8EX6hJrXofoPcEOwr4BG8aEpjqTqKY6zr3BbOEBNQpL6Tk-baxxtIS78g1qyLeHKg-yLHOE_GurAqcE0IL-4LXwt9OwDaM9Ipq5tlgMZJN83WimV6t6UbMXg4W4WVKu7nwmgSexBhIpew8a73sr1vp1rCNZMyW-2__tNE3rxb6uoMJn73UMvi1yOGtAMtFh-mkyJbnssYv3p3lmzNuQD-4erL1z4L8Au6nm0yVqxpqE8epT-kOeYicD3i1DXHt7Zh1KbP9klvDpEXUSR49QpfNWxyssFQgTd9r3v4QNlZ5uZySAkIBnQ8bnE3WaHqQaqvzQ5mq2axTOuO_qIbW9TVKouZYAeEKtOYbTGGSXrPB0-7BqmGPfWZVsGpy6R0vLe3osfzdp27XMiREH8LPTZcuef2X0Y1zD6WxJY7vImYlD50wv472QSDZA5omW-bfadJLEMYc2sOakcAvm2S055I5aAAyPIDTcuNXn0zKfTuozrA466uHwqUfekYLOp5hQNDBHvH1HhEP-aw2Eb4Myngi69Dhw7WuUJNrIQiBFsIpMJo1eyb4LVZUXfh-k6W5sOEFn-bEcITHmcEIFe-D1IdMamtb_r-lqnuldUr9lDPPTDY9-rmcedbG-ZcM3t-jItQovHlX-6ZRmGO04BjML-amViFQYIOkfZGHl7kS_KPB8JfE2KfHWO1_21tleG5lILl0clVpI_nqjlMrAUn2KEpYabYBIDDXjISLqXj7NG3V2rR4_6N43SL5ysMTADO7T6wOQwlU-zm21FIUS46gnEEExeOPCJX7OwtfUShHrtUz2HaWx_WYVc3xh_yCTBz1u2OZN0do9XSNMGYPToOEFf7JJmql7eYiurV___p9XQxMdP7jjU2u54zS_zIjPf17Lq_ETSAet4aU6eUzlWrBUce3m6Ao2eCCcHfOB-le2KE7uAFjAQGDKpZuKel0nBaH1fzF9YCMPhg4qy8_sl-_EG-DlHj4OhX3KW7jWzzCMS1RM2iVt-mVhoTLtOAHriuEX4hldF2C1gltmFCigcl--x_gFTz0veSfjAi6QiUSVGkiV-azxf8.eRInva2zbHT5eQ_AEZTd_w"

    headers = {"Authorization":refreshToken}
    
    response = requests.get('https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/refresh', headers=headers)
    json_data = json.loads(response.text)

    headers = {"Authorization":json_data}
    for badge in badges:
        url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + issuerID + "/badges/" + badge + "/issue/" + tableBody['Items'][0]["email"]
        requests.post(url, headers=headers)
    return {"Status":"200"}



    
    