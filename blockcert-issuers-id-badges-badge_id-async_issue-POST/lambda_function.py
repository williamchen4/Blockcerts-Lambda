import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.vendored import requests
import re
import botocore.response as br

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableRecipients = dynamodb.Table('blockcert.recipients')
lambda_client = boto3.client('lambda')
step_client = boto3.client('stepfunctions')
tableTest = dynamodb.Table('test')


def lambda_handler(event, context):
    
    refreshToken="Bearer eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.O20xoYZxZk0Rjxh8q5axg1PPRHU86zu5hjpnbGpnqKBAjaOnqEJmaYJ1E37ucPBkEasF_WFZ5BAFmt_qLOQvl3AbsSLqQs_QAc0aS5nXJX90ujbUrBFQcmMlOyhZzt9rv8_u-WuKIhO-wYk1JLf8Piznzl7m2ML_BVWNs558-QQoyxBU1HopNouPoK-WNWT-xR73I310KdmGD_28zJ0bRRRJuC0EH0sR3UATMIeiWkVfC3p6IIOwXbBOb3nbS-55KL8u4kokiisybozJVu0e1vT401nwn598zpwGtKGR8RO3RzKhlsEFx11Lfy8vqGqBTu0dWOHFz7snCeEwcAkzJQ.FGmkfRJCsyz5WhJ0.CG0VvasU_cjOtJaxwjPYteEhO1_ST3tMOdevLED3qKo8SpA7iGFSvDrJumYaW6pNZd5o1do99qqPNMr406K_nuTCtKIkzQygxnPkozLIsCsBVqB6Y7In9ba_4Nwy9z29zc4Bt-P58oZrLYMr4UnD47fu_zhKtHyM3UbENoq5lS_bsC3Ja9unKlnzymlv65OMiYF9hHH0G_kkZuypzdE_wt3_7GRFYw8EX6hJrXofoPcEOwr4BG8aEpjqTqKY6zr3BbOEBNQpL6Tk-baxxtIS78g1qyLeHKg-yLHOE_GurAqcE0IL-4LXwt9OwDaM9Ipq5tlgMZJN83WimV6t6UbMXg4W4WVKu7nwmgSexBhIpew8a73sr1vp1rCNZMyW-2__tNE3rxb6uoMJn73UMvi1yOGtAMtFh-mkyJbnssYv3p3lmzNuQD-4erL1z4L8Au6nm0yVqxpqE8epT-kOeYicD3i1DXHt7Zh1KbP9klvDpEXUSR49QpfNWxyssFQgTd9r3v4QNlZ5uZySAkIBnQ8bnE3WaHqQaqvzQ5mq2axTOuO_qIbW9TVKouZYAeEKtOYbTGGSXrPB0-7BqmGPfWZVsGpy6R0vLe3osfzdp27XMiREH8LPTZcuef2X0Y1zD6WxJY7vImYlD50wv472QSDZA5omW-bfadJLEMYc2sOakcAvm2S055I5aAAyPIDTcuNXn0zKfTuozrA466uHwqUfekYLOp5hQNDBHvH1HhEP-aw2Eb4Myngi69Dhw7WuUJNrIQiBFsIpMJo1eyb4LVZUXfh-k6W5sOEFn-bEcITHmcEIFe-D1IdMamtb_r-lqnuldUr9lDPPTDY9-rmcedbG-ZcM3t-jItQovHlX-6ZRmGO04BjML-amViFQYIOkfZGHl7kS_KPB8JfE2KfHWO1_21tleG5lILl0clVpI_nqjlMrAUn2KEpYabYBIDDXjISLqXj7NG3V2rR4_6N43SL5ysMTADO7T6wOQwlU-zm21FIUS46gnEEExeOPCJX7OwtfUShHrtUz2HaWx_WYVc3xh_yCTBz1u2OZN0do9XSNMGYPToOEFf7JJmql7eYiurV___p9XQxMdP7jjU2u54zS_zIjPf17Lq_ETSAet4aU6eUzlWrBUce3m6Ao2eCCcHfOB-le2KE7uAFjAQGDKpZuKel0nBaH1fzF9YCMPhg4qy8_sl-_EG-DlHj4OhX3KW7jWzzCMS1RM2iVt-mVhoTLtOAHriuEX4hldF2C1gltmFCigcl--x_gFTz0veSfjAi6QiUSVGkiV-azxf8.eRInva2zbHT5eQ_AEZTd_w"

    
    headers = {"Authorization":refreshToken}
    response = requests.get('https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/refresh', headers=headers)
    json_data = json.loads(response.text)
    headers = {"Authorization":json_data}
    
    event['params']={}
    event['params']['path']={}
    event['params']['path']['id'] = event['issuerID']
    event['params']['path']['badge_id'] = event['badgeID']
    event['body-json'] = event['data']
    
    validRecipients = []
    invalidRecipients = []
    inviteRecipients = []
    index=0
    
    # create recipient accounts if nonexistant
    while index < len(event['body-json']):
        name = str(event['body-json'][index]) + str(event['body-json'][index+1])
        email = str(event['body-json'][index+2])
        validRecipients.append(email.strip())
        data = {
            "name": name.strip(),
            "email": email.strip()
        }
        print("Event data right before post call:")
        print(event)
    
        print("post data:", data)
        print("head data:", headers)
        
        url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/recipients"
        response = requests.post(url, headers=headers, json = data)
        index += 3
    
    # issue to recipients
    for recipient in validRecipients:
        url = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + event['params']['path']['id'] + "/badges/" + event['params']['path']['badge_id'] + "/issue/" + recipient
        response = requests.post(url, headers=headers)
        if response.text[0] == '[':
            inviteRecipients.append({
                'email':recipient,
                'badges': response.json()
            })
            
    payload = {
        "issuerID": event['issuerID'],
        "inviteRecipients": inviteRecipients
    } 
    # call step functions
    try:
        step_client.start_execution(
            stateMachineArn='arn:aws:states:us-west-2:010063476047:stateMachine:InviteEmails',
            input = json.dumps(payload)
        )
    except Exception as e:
        test.put_item({'id':str(e)})
    
    '''
    index = 0
    while index <  len(inviteRecipients):
        data = {
            'data':inviteRecipients[index:index+10],
            'issuerID':event['params']['path']['id']
        }
        index += 10
    '''  
    #lambda_client.invoke(FunctionName="blockcert-recipients-invite-issuer_id-POST", InvocationType='Event', Payload=json.dumps(data))
    #test.put_item(Item={'id':9999, 'e':invoke_response['Payload'].read()})
    #return 200
    #return 