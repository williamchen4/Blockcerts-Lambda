import json
import boto3
import urllib.request
import sys
from io import BytesIO
import urllib
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.issuers')
s3 = boto3.resource('s3', region_name='us-west-2')
tableBadges = dynamodb.Table('blockcert.badges')

def lambda_handler(event, context):
    
    issuerID = event['body-json']['issuerID']
    tableBody = table.query(
    KeyConditionExpression=Key('id').eq(issuerID)
    )
    issuerImage = tableBody['Items'][0]['image']
    description = event['body-json']['description']
    badgeImage = event['body-json']['badgeImage']
    badgeName = event['body-json']['badgeName']
    recipientName = event['body-json']['recipientName']
    date1 = event['body-json']['date'][0:10]
    date = date1[5:] + "-" + date1[0:4]
    signature = event['body-json']['signature']

    if int(event['body-json']['template']) % 2 == 0:
        temp = issuerImage
        issuerImage = badgeImage
        badgeImage = temp

    html_str12 = """
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
                    background-image: url(https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/cert12.png);
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
                    top: 350px;
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
                    top: 693px;
                    width:200px;
                    filter: brightness(0) invert(1);
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
                    text-align:center;
                }
            </style>
        </head>
        
        <body>
            <h1 class='cert-name'><span style='font-weight:normal'>""" + badgeName + """</span></h1>
            <img class='logo' src=' """ + issuerImage + """ ' height='42' width='42'>
            <img class='badge' src=' """ + badgeImage + """ ' height='42' width='42'>
            <p class='description'>""" + description + """</p>
            <h1 class='recipient-name'><span style='font-weight:normal'>""" + recipientName + """</span></h1>
            <p class='date'>""" + date + """</p>
            <img class='signature' src=' """ + signature + """ '>
        </body>
        </html>
    """
        
    html_str34 = """
    <!DOCTYPE html>
    <html>
            <link href="https://fonts.googleapis.com/css?family=Lobster" rel="stylesheet">
    <head>
        <meta charset="UTF-8">
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
                background-image: url(https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/cert34.jpg);
                background-repeat: no-repeat;
                background-size: 100%;
                position: relative;
                color: 	#000000;
                font-family: 'Lobster', cursive;
            }
            .cert-name{
                position: absolute;
                left: 50%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 264px;

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
                left: 50%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 744px;
                height: 150px;
                width: 150px;        
            }
            .logo{
                position: absolute;
                left: 50%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 120px;
                height: 150px;
                width: 150px;
            }
            .date{
                position: absolute;
                left: 25%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 714px;
            }
            .signature{
                position: absolute;
                left: 72%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 690px;
                width: 200px
            }
            .recipient-name{
                position: absolute;
                left: 50%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 450px;
            }
            .description{
                position: absolute;
                left: 50%;
                -webkit-transform: translateX(-50%);
                transform: translateX(-50%);
                top: 547px;
                max-width: 100ch; 
                text-align:center;
            }
        </style>
    </head>
    
    <body>
        <h1 class='cert-name'><span style='font-weight:normal'>""" + badgeName + """</span></h1>
        <img class='badge' src=' """ + badgeImage + """ 'height='42' width='42'>
        <img class='logo' src=' """ + issuerImage + """ 'height='42' width='42'>
        <p class='acknowledgement'>This certificate is presented to</p>
        <p class='description'>""" + description + """</p>
        <h1 class='recipient-name'><span style='font-weight:normal'>""" + recipientName + """</span></h1>
        <p class='date'>""" + date + """</p>
        <img class='signature' src=' """ + signature + """ '>
    </body>
    </html>
    """


    html_str56 = """
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
            background-image: url(https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/cert56.jpg);
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
        .logo{
            position: absolute;
            left: 49.5%;
            -webkit-transform: translateX(-50%);
            transform: translateX(-50%);
            top: 673px;
            height: 150px;
            width: 150px;
        }
        .badge{
            position: absolute;
            left: 49%;
            -webkit-transform: translateX(-50%);
            transform: translateX(-50%);
            top: 150px;
            height: 150px;
            width: 150px;
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
            top: 691px;
            width:150px
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
            text-align:center;
        }
        </style>
        </head>
        
        <body>
        <h1 class='cert-name'><span style='font-weight:normal'>""" + badgeName + """</span></h1>
        <h1 class='recipient-name'><span style='font-weight:normal'>""" + recipientName + """</span></h1>
        <img class='logo' src=' """ + issuerImage + """ '  height='42' width='42'>
        <img class='badge' src=' """ + badgeImage + """ ' height='42' width='42'>
        <p class='description'>""" + description + """</p>
        <p class='date'>""" + date + """</p>
        <img class='signature' src=' """ + signature + """ '>
        </body>
        </html>
    """

    html_str12 = html_str12.replace('\n', ' ')
    html_str12 = html_str12.replace('\t', ' ')
    html_str34 = html_str34.replace('\n', ' ')
    html_str34 = html_str34.replace('\t', ' ')
    html_str56 = html_str56.replace('\n', ' ')
    html_str56 = html_str56.replace('\t', ' ')

    template = event['body-json']['template']
    if template == "1" or template == "2":
        return html_str12
    elif template == "3" or template == "4":
        return html_str34
    else:
        return html_str56