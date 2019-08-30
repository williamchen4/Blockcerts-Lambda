import json
import smtplib
import boto3
import random
from boto3.dynamodb.conditions import Key, Attr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('blockcert.invites')
tableRecipients = dynamodb.Table('blockcert.recipients')

def getNonce():
    nonce = random.randint(100000, 999999)
    tableBody = table.query(
    KeyConditionExpression=Key('id').eq(str(nonce))
    )
    while tableBody['Count'] != 0:
        nonce = random.randint(100000, 999999)
        tableBody = table.query(
        KeyConditionExpression=Key('id').eq(str(nonce))
        )
    return str(nonce)
        
def sendEmail(nonce, link, recipient):
    me = "digitalbadges@mail.fresnostate.edu"
    you = recipient
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Fresno State Certificate Invitation"
    msg['From'] = me
    msg['To'] = you

    html = '''<html>
        <head>
        <meta name="viewport" content="width=device-width" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Simple Transactional Email</title>
        <style>
            img {{
                border: none;
                -ms-interpolation-mode: bicubic;
                max-width: 100%;
            }}
            body {{
                background-color: #f6f6f6;
                font-family: sans-serif;
                -webkit-font-smoothing: antialiased;
                font-size: 14px;
                line-height: 1.4;
                margin: 0;
                padding: 0;
                -ms-text-size-adjust: 100%;
                -webkit-text-size-adjust: 100%;
            }}
            table {{
                border-collapse: separate;
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                width: 100%; }}
                table td {{
                font-family: sans-serif;
                font-size: 14px;
                vertical-align: top;
            }}
            /* -------------------------------------
                BODY & CONTAINER
            ------------------------------------- */
            .body {{
                background-color: #f6f6f6;
                width: 100%;
            }}
            /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
            .container {{
                display: block;
                Margin: 0 auto !important;
                /* makes it centered */
                max-width: 700px;
                padding: 10px;
                width: 700px;
            }}
            /* This should also be a block element, so that it will fill 100% of the .container */
            .content {{
                box-sizing: border-box;
                display: block;
                Margin: 0 auto;
                max-width: 700px;
                padding: 10px;
            }}
            /* -------------------------------------
                HEADER, FOOTER, MAIN
            ------------------------------------- */
            .main {{
                background: #ffffff;
                border-radius: 3px;
                width: 100%;
            }}
            .wrapper {{
                box-sizing: border-box;
                padding: 20px;
            }}
            .content-block {{
                padding-bottom: 10px;
                padding-top: 10px;
            }}
            .footer {{
                clear: both;
                Margin-top: 10px;
                text-align: center;
                width: 100%;
            }}
                .footer td,
                .footer p,
                .footer span,
                .footer a {{
                color: #999999;
                font-size: 12px;
                text-align: center;
            }}
            /* -------------------------------------
                TYPOGRAPHY
            ------------------------------------- */
            h1,
            h2,
            h3,
            h4 {{
                color: #000000;
                font-family: sans-serif;
                font-weight: 400;
                line-height: 1.4;
                margin: 0;
                margin-bottom: 30px;
            }}
            h1 {{
                font-size: 35px;
                font-weight: 300;
                text-align: center;
                text-transform: capitalize;
            }}
            h2 {{
            display:inline;
            }}
        
            p,
            ul,
            ol {{
                font-family: sans-serif;
                font-size: 16px;
                font-weight: normal;
                margin: 0;
                margin-bottom: 15px;
            }}
                p li,
                ul li,
                ol li {{
                list-style-position: inside;
                margin-left: 2px;
            }}
            a {{
                color: #3498db;
                text-decoration: underline;
            }}
            /* -------------------------------------
                BUTTONS
            ------------------------------------- */
            .btn {{
                box-sizing: border-box;
                width: 100%; }}
                .btn > tbody > tr > td {{
                padding-bottom: 15px; }}
                .btn table {{
                width: auto;
            }}
                .btn table td {{
                background-color: #ffffff;
                border-radius: 5px;
                text-align: center;
            }}
                .btn a {{
                background-color: #ffffff;
                border: solid 1px #3498db;
                border-radius: 5px;
                box-sizing: border-box;
                color: #3498db;
                cursor: pointer;
                display: inline-block;
                font-size: 14px;
                font-weight: bold;
                margin: 0;
                padding: 12px 25px;
                text-decoration: none;
                text-transform: capitalize;
            }}
            .btn-primary table td {{
                background-color: #3498db;
            }}
            .btn-primary a {{
                background-color: #3498db;
                border-color: #3498db;
                color: #ffffff;
            }}
            /* -------------------------------------
                OTHER STYLES THAT MIGHT BE USEFUL
            ------------------------------------- */
            .last {{
                margin-bottom: 0;
            }}
            .first {{
                margin-top: 0;
            }}
            .align-center {{
                text-align: center;
            }}
            .align-right {{
                text-align: right;
            }}
            .align-left {{
                text-align: left;
            }}
            .clear {{
                clear: both;
            }}
            .mt0 {{
                margin-top: 0;
            }}
            .mb0 {{
                margin-bottom: 0;
            }}
            .preheader {{
                color: transparent;
                display: none;
                height: 0;
                max-height: 0;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                mso-hide: all;
                visibility: hidden;
                width: 0;
            }}
            .powered-by a {{
                text-decoration: none;
            }}
            hr {{
                border: 1;
                border-bottom: 1px solid #f6f6f6;
                margin: 20px 0;
            }}
            /* -------------------------------------
                RESPONSIVE AND MOBILE FRIENDLY STYLES
            ------------------------------------- */
            @media only screen and (max-width: 620px) {{
                table[class=body] h1 {{
                font-size: 28px !important;
                margin-bottom: 10px !important;
                }}
                table[class=body] p,
                table[class=body] ul,
                table[class=body] ol,
                table[class=body] td,
                table[class=body] span,
                table[class=body] a {{
                font-size: 16px !important;
                }}
                table[class=body] .wrapper,
                table[class=body] .article {{
                padding: 10px !important;
                }}
                table[class=body] .content {{
                padding: 0 !important;
                }}
                table[class=body] .container {{
                padding: 0 !important;
                width: 100% !important;
                }}
                table[class=body] .main {{
                border-left-width: 0 !important;
                border-radius: 0 !important;
                border-right-width: 0 !important;
                }}
                table[class=body] .btn table {{
                width: 100% !important;
                }}
                table[class=body] .btn a {{
                width: 100% !important;
                }}
                table[class=body] .img-responsive {{
                height: auto !important;
                max-width: 100% !important;
                width: auto !important;
                }}
            }}
            /* -------------------------------------
                PRESERVE THESE STYLES IN THE HEAD
            ------------------------------------- */
            @media all {{
                .ExternalClass {{
                width: 100%;
                }}
                .ExternalClass,
                .ExternalClass p,
                .ExternalClass span,
                .ExternalClass font,
                .ExternalClass td,
                .ExternalClass div {{
                line-height: 100%;
                }}
                .apple-link a {{
                color: inherit !important;
                font-family: inherit !important;
                font-size: inherit !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                text-decoration: none !important;
                }}
                .btn-primary table td:hover {{
                background-color: #34495e !important;
                }}
                .btn-primary a:hover {{
                background-color: #34495e !important;
                border-color: #34495e !important;
                }}
            }}
            </style>
        </head>
        <body>
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
        <tr>
            <td>&nbsp;</td>
            <td class="container">
            <div class="content">
                <span class="preheader">Open to claim your Blockcerts certificate!</span>
                <table role="presentation" class="main">
                <tr>
                    <td class="wrapper">
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                        <td>
                            <h2><strong>You've been awarded a Fresno State Badge!</strong></h2>
                            <br>
                            To receive your badge and certificate, download the Blockcerts mobile app. For first-time setup help, <a href="https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/Steps">click here</a>.
                            <br><br>
                            <ul>
                                <li>When prompted, copy the following URL: <br>
                                {0}</li>
                                <li>Your one-time code is: <strong>{1}</strong></li>
                            </ul>
                            <br><br><br>
                            <h2><strong>What is Blockcerts?</strong></h2>
                            <br>
                            Blockcerts are digital credentials issued to the Bitcoin Blockchain. Such credentials have the benefit of being tamper-proof, instantly verifiable, and sharable with others. Visit the <a href="https://www.blockcerts.org/">Blockcerts website</a> for more information.
                            <div style="text-align:center">
                                <div style="display:inline-block; margin:5px 20px; padding:5px;">
                                    <a href="https://itunes.apple.com/us/app/blockcerts-wallet/id1146921514?mt=8"><img src="https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/ios.png" style=" display: inline-block; width:188px; height:auto;"/></a>  
                                </div>
                                <div style="display:inline-block; margin:5px 20px; padding:5px;">
                                    <a href='https://play.google.com/store/apps/details?id=com.learningmachine.android.app&hl=en_US&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img alt='Get it on Google Play' src='https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/android.png' style="width:188px; height:auto; display:inline-block; "/></a>   
                                </div>
                                <br><br>
                                <hr style="border-color:red">
                                <img src="https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/fslogo.png" style="width:300px; display: block; margin: 0 auto;">
                            </div>
                        </td>
                    </tr>
                </table>
                </td>
            </tr>
            </table>
        </div>
        </td>
        <td>&nbsp;</td>
        </tr>
        </table>
    </body>
    </html>'''.format(link, nonce)

    part2 = MIMEText(html, 'html')
    
    msg.attach(part2)
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.ehlo()

    password = 'X;IbRtogC2KvcctMsbx;jzQLLp4Mm+Lu'
    mail.login('digitalbadges@mail.fresnostate.edu', 'Password1@')
    mail.sendmail(me, you, msg.as_string())
    mail.quit()


def lambda_handler(event, context):
    
    print(event)

    # get recipient email
    tableBody = tableRecipients.query(
    KeyConditionExpression=Key('id').eq(event['params']['id'])
    )
    recipientEmail = tableBody['Items'][0].get('email')
    
    # get nonce
    nonce = getNonce()
    link = "https://tqud77gtrh.execute-api.us-west-2.amazonaws.com/default/issuers/" + event['params']['issuer_id']
    sendEmail(nonce, link, recipientEmail)
    
    data = {
        "id":nonce,
        "recipient_id":event['params']['id'],
        "issuer_id":event['params']['issuer_id'],
        "badges":event['body']
    }
    table.put_item(Item=data)
    return nonce