import json
import boto3
import urllib.request
import sys
from io import BytesIO
import urllib
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('tableTest')
s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket('fswillc1')
bucket2 = s3.Bucket('fs.blockcerts.poc')
tableBadges = dynamodb.Table('blockcert.badges')

def lambda_handler(event, context):
    
    recipientName = event['body-json']['recipientName']
    description = event['body-json']['description']
    badgeImage = event['body-json']['badgeImage']
    badgeName = event['body-json']['badgeName']
    date1 =  event['body-json']['date'][0:10]
    date = date1[5:] + "-" + date1[0:4]
    signature = event['body-json']['signature']
    
    '''
    link = 1
    mList = []
    for a in bucket2.objects.all():
         if event['params']['path']['id'] in str(a):
            link = "https://s3-us-west-2.amazonaws.com/fs.blockcerts.poc/" + str(a.key)
            f = urllib.request.urlopen(link)
            myfile = f.read()
            d = json.loads(myfile)
            recipientName = d['recipientProfile']['name']
            description = d['badge']['description']
            badgeImage = d['badge']['image']
            badgeName = d['badge']['name']
            date1 = str(d['issuedOn'])[0:10]
            date = date1[5:] + "-" + date1[0:4]
            signature = d['badge']['signatureLines'][0]['name']

            tableBody = tableBadges.query(
            KeyConditionExpression=Key('id').eq(d['badge']['id'][9:])
            )
            break
    '''
    
    
    fsLogo = "https://upload.wikimedia.org/wikipedia/en/thumb/d/df/California_State_University%2C_Fresno_seal.svg/1200px-California_State_University%2C_Fresno_seal.svg.png"
    fsBanner = "https://s3-us-west-2.amazonaws.com/fswillc1/images/1.png"
    template = tableBody['Items'][0].get('template')
    
    html_str1 ="""
     <!DOCTYPE html>
        <html>
        <head>
        <link href='https://fonts.googleapis.com/css?family=Lobster' rel='stylesheet'>
            <meta charset='UTF-8'>
            <title>title</title>
        
            <style>html,body,div,span,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,b,u,i,center,
                    {
                    margin: 0;
                    padding: 0;
                    border: 0;
                    font-size: 100%;
                    font: inherit;
                    vertical-align: baseline;
        
                }
        
                html,
                body {
                    max-height: 1000px;
                    max-width: 1333px;
                    min-height: 1000px;
                    min-width: 1333px;
                }
        
                body {
                    background-image: url(https://s3-us-west-2.amazonaws.com/fswillc1/images/cert7.jpg);
                    background-repeat: no-repeat;
                    background-size: 100%;
                    position: relative;
                    color: #033b72;
                    font-family: 'Lobster', cursive;
                }
        
                .cert-name {
                    position: absolute;
                    left: 49%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 302px;
        
                }
        
                .badge {
                    position: absolute;
                    left: 49.5%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 725px;
                    height: 140px;
                    width: 140px;
                }
                .acknowledgement{
                    position: absolute;
                    left: 49%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 419px;
                }
                .logo {
                    position: absolute;
                    left: 51%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 100px;
                    height: 209px;
                    width: 319px;
                }
        
                .date {
                    position: absolute;
                    left: 26%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 750px;
                }
                .date2 {
                    position: absolute;
                    left: 26%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 800px;  
                }
                .signature {
                    position: absolute;
                    left: 73%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 750px;
                }
                .signature2 {
                    position: absolute;
                    left: 73%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 800px;
                }
                .recipient-name {
                    position: absolute;
                    left: 49%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 466px;
                }
        
                .description {
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 586px;
                    max-width: 100ch;
                }
            </style>
        </head>
        
        <body>
            <h1 class='cert-name'><strong>""" + badgeName + """</strong></h1>
            <h1 class='recipient-name'>""" + recipientName + """</h1>
                <img class='badge' src=' """ + badgeImage + """ ' height='105' width='146'>
                <img class='logo' src='https://s3-us-west-2.amazonaws.com/fswillc1/images/bulldog.png' height='105' width='146'>
                <p class='description'>""" + description + """</p>
                <p class='date'>""" + date + """ </p>
                <p class='signature'>""" + signature + """</p>
                <p class='acknowledgement'>This certificate is presented to</p>
                <p class='date2'>DATE</p>
                <p class='signature2'>SIGNATURE</p>
        </body>
        </html>"""
    html_str2 = """
        <!DOCTYPE html>
        <html>
        <link href='https://fonts.googleapis.com/css?family=Lobster' rel='stylesheet'>
        <head>
            <meta charset='UTF-8'>
            <title>title</title>
        
            <style>html,body,div,span,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,b,u,i,
                center,
                    {
                    margin: 0;
                    padding: 0;
                    border: 0;
                    font-size: 100%;
                    font: inherit;
                    vertical-align: baseline;
        
                }
                html, body {
                    max-height: 1000px;
                    max-width: 1333px;
                    min-height: 1000px;
                    min-width: 1333px;
                }
        
                body {
                    background-image: url(https://s3-us-west-2.amazonaws.com/fswillc1/cert2.png);
                    background-repeat: no-repeat;
                    background-size: 100%;
                    position: relative;
                    color: #c2c2c2;
                    font-family: 'Lobster', cursive;
                }
                .cert-name{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 264px;
        
                }
                .badge{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 348px;
                    height: 130px;
                    width: 130px;        
                }
                .logo{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 700px;
                    height: 130px;
                    width: 130px;     
                }
                .date{
                    position: absolute;
                    left: 30%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 714px;
                }
                .signature{
                    position: absolute;
                    left: 69%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 714px;
                }
                .recipient-name{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 464px;
                }
                .description{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 550px;
                }
            </style>
        </head>
        
        <body>
            <h1 class='cert-name'><span style='font-weight:normal'>""" + badgeName + """</span></h1>
            <h2 class='recipient-name'><span style="font-weight:normal">""" + recipientName + """</span></h1>
            <img class='logo' src=' """ + fsLogo + """ ' height='42' width='42'>
            <img class='badge' src=' """ + badgeImage + """ ' height='42' width='42'>
        
            <p class='description'>""" + description + """</p>
            <p class='date'>""" + date + """</p>
            <p class='signature'>""" + signature + """</p>
        </body>
        </html>"""
        
    
    html_str3 = """
    <!DOCTYPE html>
        <html>
                <link href='https://fonts.googleapis.com/css?family=Lobster' rel='stylesheet'>
        <head>
            <meta charset='UTF-8'>
            <title>title</title>
        
            <style>html,body,div,span,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,b,u,i,
                center,
                    {
                    margin: 0;
                    padding: 0;
                    border: 0;
                    font-size: 100%;
                    font: inherit;
                    vertical-align: baseline;
        
                }
                html, body {
                    max-height: 1000px;
                    max-width: 1333px;
                    min-height: 1000px;
                    min-width: 1333px;
                }
        
                body {
                    background-image: url(https://s3-us-west-2.amazonaws.com/fswillc1/images/cert9.jpg);
                    background-repeat: no-repeat;
                    background-size: 100%;
                    position: relative;
                    color: 	#000000;
                    font-family: 'Lobster', cursive;
                }
                .cert-name{
                    position: absolute;
                    left: 49%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 303px;

                }
                .acknowledgement{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 384px;  
                }
                .badge{
                    position: absolute;
                    left: 49.5%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 673px;
                    height: 150px;
                    width: 150px;
                }
                .logo{
                    position: absolute;
                    left: 50%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 191px;
                    height: 57px;
                    width: 433px;
                }
                .date{
                    position: absolute;
                    left: 21.5%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 699px;
                }
                .signature{
                    position: absolute;
                    left: 76.5%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 699px;
                }
                .recipient-name{
                    position: absolute;
                    left: 49.5%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 450px;
                }
                .description{
                    position: absolute;
                    left: 49.7%;
                    -webkit-transform: translateX(-50%);
                    transform: translateX(-50%);
                    top: 573px;
                    max-width: 140ch; 
                }
            </style>
        </head>
        
        <body>
            <h1 class='cert-name'><span style='font-weight:normal'>""" + badgeName + """</span></h1>
            <h1 class='recipient-name'><span style='font-weight:normal'>""" + recipientName + """</span></h1>
            <img class='logo' src='https://s3-us-west-2.amazonaws.com/fswillc1/images/1.png' height='42' width='42'>
            <img class='badge' src=' """ + badgeImage + """ ' height='42' width='42'>
            <p class='description'>""" + description + """</p>
            <p class='date'>""" + date + """</p>
            <p class='signature'>""" + signature + """</p>
        </body>
        </html>
    """
    html_str1 = html_str1.replace('\n', ' ')
    html_str1 = html_str1.replace('\t', ' ')
    html_str2 = html_str2.replace('\n', ' ')
    html_str2 = html_str1.replace('\t', ' ')
    html_str3 = html_str3.replace('\n', ' ')
    html_str3 = html_str1.replace('\t', ' ')

    return html_str3
    Html_file= open("/tmp/filename",'w')
    html_str = "1"
    if template == "1":
        html_str = html_str1
    elif template == "2":
        html_str = html_str2
    else:
        html_str = html_str3
        
    Html_file.write(html_str)
    Html_file.close()

    string = html_str
    encoded_string = string.encode("utf-8")

    bucket_name = "fswillc1"
    file_name = str(event['params']['path']['id']) + ".html"
    lambda_path = "/tmp/" + file_name
    s3_path = "display/" + file_name

    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string, ContentType='text/html')
    
    object_acl = s3.ObjectAcl('fswillc1', s3_path)
    response = object_acl.put(ACL='public-read')
