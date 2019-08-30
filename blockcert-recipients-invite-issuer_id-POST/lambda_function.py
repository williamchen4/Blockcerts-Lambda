import json
import smtplib
import boto3
import random
from boto3.dynamodb.conditions import Key, Attr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
tableInvites = dynamodb.Table('blockcert.invites')
tableRecipients = dynamodb.Table('blockcert.recipients')
test = dynamodb.Table('test')

def getNonce():
    nonce = random.randint(100000, 999999)
    tableBody = tableInvites.query(KeyConditionExpression=Key('id').eq(str(nonce)))
    while tableBody['Count'] != 0:
        nonce = random.randint(100000, 999999)
        tableBody = table.query(
        KeyConditionExpression=Key('id').eq(str(nonce))
        )
    return str(nonce)

def lambda_handler(event, context):
    #test.put_item(Item={'id':event['data'][0]})
    #event['body-json']=event['body-json']['data'] 
    
    print(event)
    
    
    '''
    tableBodyInvites = tableInvites.scan()
    for i in tableBodyInvites['Items']:
        if i['issuer_id']==event['issuerID'] and i['recipient_email']==event['body-json'][0]['email']:
            return
    '''
    
    link = "https://badges.fresnostate.edu/issuers/" + event['issuerID']
    me = "digitalbadges@mail.fresnostate.edu"

    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.starttls()
    password = 'X;IbRtogC2KvcctMsbx;jzQLLp4Mm+Lu'
    mail.login('digitalbadges@mail.fresnostate.edu', 'Password1@')

    htmlTemplate = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html style="width:100%;font-family:arial, 'helvetica neue', helvetica, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0;">
 <head>
  <meta charset="UTF-8">
  <meta content="width=device-width, initial-scale=1" name="viewport">
  <meta name="x-apple-disable-message-reformatting">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta content="telephone=no" name="format-detection">
  <title>uBadges Invite Email</title>
  <!--[if (mso 16)]>
    <style type="text/css">
    a {{text-decoration: none;}}
    </style>
    <![endif]-->
  <!--[if gte mso 9]><style>sup {{ font-size: 100% !important; }}</style><![endif]-->
  <style type="text/css">
@media only screen and (max-width:600px) {{p, ul li, ol li, a {{ font-size:16px!important; line-height:150%!important }} h1 {{ font-size:30px!important; text-align:center; line-height:120%!important }} h2 {{ font-size:26px!important; text-align:center; line-height:120%!important }} h3 {{ font-size:20px!important; text-align:center; line-height:120%!important }} h1 a {{ font-size:30px!important }} h2 a {{ font-size:26px!important }} h3 a {{ font-size:20px!important }} .es-menu td a {{ font-size:16px!important }} .es-header-body p, .es-header-body ul li, .es-header-body ol li, .es-header-body a {{ font-size:16px!important }} .es-footer-body p, .es-footer-body ul li, .es-footer-body ol li, .es-footer-body a {{ font-size:16px!important }} .es-infoblock p, .es-infoblock ul li, .es-infoblock ol li, .es-infoblock a {{ font-size:12px!important }} *[class="gmail-fix"] {{ display:none!important }} .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3 {{ text-align:center!important }} .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3 {{ text-align:right!important }} .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3 {{ text-align:left!important }} .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img {{ display:inline!important }} .es-button-border {{ display:block!important }} a.es-button {{ font-size:20px!important; display:block!important; border-left-width:0px!important; border-right-width:0px!important }} .es-btn-fw {{ border-width:10px 0px!important; text-align:center!important }} .es-adaptive table, .es-btn-fw, .es-btn-fw-brdr, .es-left, .es-right {{ width:100%!important }} .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header {{ width:100%!important; max-width:600px!important }} .es-adapt-td {{ display:block!important; width:100%!important }} .adapt-img {{ width:100%!important; height:auto!important }} .es-m-p0 {{ padding:0px!important }} .es-m-p0r {{ padding-right:0px!important }} .es-m-p0l {{ padding-left:0px!important }} .es-m-p0t {{ padding-top:0px!important }} .es-m-p0b {{ padding-bottom:0!important }} .es-m-p20b {{ padding-bottom:20px!important }} .es-mobile-hidden, .es-hidden {{ display:none!important }} .es-desk-hidden {{ display:table-row!important; width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important }} .es-desk-menu-hidden {{ display:table-cell!important }} table.es-table-not-adapt, .esd-block-html table {{ width:auto!important }} table.es-social {{ display:inline-block!important }} table.es-social td {{ display:inline-block!important }} }}
#outlook a {{
	padding:0;
}}
.ExternalClass {{
	width:100%;
}}
.ExternalClass,
.ExternalClass p,
.ExternalClass span,
.ExternalClass font,
.ExternalClass td,
.ExternalClass div {{
	line-height:100%;
}}
.es-button {{
	mso-style-priority:100!important;
	text-decoration:none!important;
}}
a[x-apple-data-detectors] {{
	color:inherit!important;
	text-decoration:none!important;
	font-size:inherit!important;
	font-family:inherit!important;
	font-weight:inherit!important;
	line-height:inherit!important;
}}
.es-desk-hidden {{
	display:none;
	float:left;
	overflow:hidden;
	width:0;
	max-height:0;
	line-height:0;
	mso-hide:all;
}}
</style>
 </head>
 <body style="width:100%;font-family:arial, 'helvetica neue', helvetica, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0;">
  <div class="es-wrapper-color" style="background-color:#D0CCCC;">
   <!--[if gte mso 9]>
			<v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
				<v:fill type="tile" color="#d0cccc"></v:fill>
			</v:background>
		<![endif]-->
   <table class="es-wrapper" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top;" width="100%" cellspacing="0" cellpadding="0">
     <tr style="border-collapse:collapse;">
      <td valign="top" style="padding:0;Margin:0;">
       <table class="es-content es-mobile-hidden" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;">
         <tr style="border-collapse:collapse;">
          <td align="center" style="padding:0;Margin:0;">
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;" width="600" cellspacing="0" cellpadding="0" align="center">
             <tr style="border-collapse:collapse;">
              <td style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:20px;padding-right:20px;background-position:left top;" align="left">
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                 <tr style="border-collapse:collapse;">
                  <td class="es-m-p0r" width="560" valign="top" align="center" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td class="es-infoblock es-m-txt-c" align="left" style="padding:0;Margin:0;line-height:14px;font-size:12px;color:#CCCCCC;"> <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:12px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:14px;color:#626161;">Open the claim your Fresno State uBadge!</p> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table> </td>
             </tr>
           </table> </td>
         </tr>
       </table>
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%;">
         <tr style="border-collapse:collapse;">
          <td align="center" style="padding:0;Margin:0;">
           <table class="es-content-body" width="600" cellspacing="0" cellpadding="0" bgcolor="#ffffff" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:#FFFFFF;">
             <tr style="border-collapse:collapse;">
              <td align="left" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;">
               <!--[if mso]><table width="560" cellpadding="0" cellspacing="0"><tr><td width="270" valign="top"><![endif]-->
               <table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left;">
                 <tr style="border-collapse:collapse;">
                  <td width="270" valign="top" align="center" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="center" style="padding:0;Margin:0;"> <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:48px;font-family:verdana, geneva, sans-serif;line-height:72px;color:#333333;"><span style="color:#C41230;">u</span><span style="color:#002C76;">Badges</span></p> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table>
               <!--[if mso]></td><td width="20"></td><td width="270" valign="top"><![endif]-->
               <table class="es-right" cellspacing="0" cellpadding="0" align="right" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:right;">
                 <tr style="border-collapse:collapse;">
                  <td width="270" valign="top" align="center" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="center" style="padding:0;Margin:0;"> <img class="adapt-img" src="https://janrl.stripocdn.email/content/guids/CABINET_ea553439354f67907ca5668315cd7f57/images/72541560958314446.jpg" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;width:270px;" width="270"></td>
                     </tr>
                   </table> </td>
                 </tr>
               </table>
               <!--[if mso]></td></tr></table><![endif]--> </td>
             </tr>
             <tr style="border-collapse:collapse;">
              <td style="Margin:0;padding-top:20px;padding-bottom:20px;padding-left:20px;padding-right:20px;background-position:left top;" align="left">
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                 <tr style="border-collapse:collapse;">
                  <td width="560" valign="top" align="center" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="center" style="padding:0;Margin:0;padding-bottom:20px;padding-left:20px;padding-right:20px;">
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                         <tr style="border-collapse:collapse;">
                          <td style="padding:0;Margin:0px 0px 0px 0px;border-bottom:1px solid #CCCCCC;background:none;height:1px;width:100%;margin:0px;"></td>
                         </tr>
                       </table> </td>
                     </tr>
                     <tr style="border-collapse:collapse;">
                      <td align="left" style="padding:0;Margin:0;padding-top:15px;"> <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:18px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:27px;color:#333333;text-align:center;"><strong><span style="font-size:28px;">You've been awarded a Fresno State Canvas Badge!</span> </strong><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;"><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;text-align:center;">Here is the information needed to setup your Blockcerts Wallet mobile app.</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;text-align:center;"><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;text-align:center;"><strong>Issuer URL</strong>: {0}</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;text-align:center;">Your <strong>one-time code</strong> is: {1}</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;text-align:center;"><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:16px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:24px;color:#333333;text-align:center;"><strong>🌟 Be on the lookout for another email with instructions for claiming your Canvas Badge!</strong></p> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table> </td>
             </tr>
             <tr style="border-collapse:collapse;">
              <td style="padding:0;Margin:0;padding-bottom:20px;padding-left:20px;padding-right:20px;background-position:left top;" align="left">
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                 <tr style="border-collapse:collapse;">
                  <td width="560" valign="top" align="center" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="left" style="padding:0;Margin:0;"> <p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:16px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:24px;color:#333333;"><strong>What is Blockcerts?</strong></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;">Blockcerts are digital credentials issued to the Bitcoin Blockchain. Such credentials have the benefit of being tamper-proof, instantly verifiable, and sharable with others.</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;"><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;">Visit the <a target="_blank" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;font-size:14px;text-decoration:underline;color:#1376C8;line-height:21px;" href="https://www.blockcerts.org/">Blockcerts website</a> for more information or download the Blockcerts Wallet app for your mobile device from one the links below.</p> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table> </td>
             </tr>
             <tr style="border-collapse:collapse;">
              <td style="padding:0;Margin:0;padding-left:20px;padding-right:20px;background-position:left top;" align="left">
               <!--[if mso]><table width="560" cellpadding="0" cellspacing="0"><tr><td width="278" valign="top"><![endif]-->
               <table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left;">
                 <tr style="border-collapse:collapse;">
                  <td class="es-m-p20b" width="278" align="left" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="center" style="padding:0;Margin:0;"> <a target="_blank" href="https://itunes.apple.com/us/app/blockcerts-wallet/id1146921514?mt=8" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;font-size:14px;text-decoration:underline;color:#1376C8;"> <img src="https://janrl.stripocdn.email/content/guids/CABINET_ea553439354f67907ca5668315cd7f57/images/88991558459021099.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;" width="180"> </a> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table>
               <!--[if mso]></td><td width="0"></td><td width="282" valign="top"><![endif]-->
               <table class="es-right" cellspacing="0" cellpadding="0" align="right" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:right;">
                 <tr style="border-collapse:collapse;">
                  <td width="282" align="left" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="center" style="padding:0;Margin:0;"> <a target="_blank" href="https://play.google.com/store/apps/details?id=com.learningmachine.android.app&hl=en_US&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;font-size:14px;text-decoration:underline;color:#1376C8;"> <img src="https://janrl.stripocdn.email/content/guids/CABINET_ea553439354f67907ca5668315cd7f57/images/85051558459040364.png" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;" width="180"> </a> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table>
               <!--[if mso]></td></tr></table><![endif]--> </td>
             </tr>
             <tr style="border-collapse:collapse;">
              <td style="padding:0;Margin:0;padding-bottom:20px;padding-left:20px;padding-right:20px;background-position:left top;" align="left">
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                 <tr style="border-collapse:collapse;">
                  <td width="560" valign="top" align="center" style="padding:0;Margin:0;">
                   <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                     <tr style="border-collapse:collapse;">
                      <td align="center" style="padding:20px;Margin:0;">
                       <table width="100%" height="100%" cellspacing="0" cellpadding="0" border="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                         <tr style="border-collapse:collapse;">
                          <td style="padding:0;Margin:0px 0px 0px 0px;border-bottom:1px solid #CCCCCC;background:none;height:1px;width:100%;margin:0px;"></td>
                         </tr>
                       </table> </td>
                     </tr>
                     <tr style="border-collapse:collapse;">
                      <td align="left" style="padding:0;Margin:0;font-size:16px;"> <strong>If this is the first time you're receiving this email, you will need to setup your Blockcerts Wallet mobile app. Follow the instructions below to get setup.</strong>
                       <ol>
                        <li style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;Margin-bottom:15px;color:#333333;">Download the app from your device's app store. You can click one the download links at the bottom of the email to down the app for your device.</li>
                        <li style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;Margin-bottom:15px;color:#333333;">Open the <strong>Blockcerts</strong> app and click <strong>Continue</strong>.<br><br>You will need to backup the passphrase generated by the app. This passphrase is used to recover your badges in case you uninstall the app.</li>
                        <li style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;Margin-bottom:15px;color:#333333;">Select <strong>Manual Hard Copy </strong>and manually write the code provided on a piece of paper or select <strong>Copy to Email or Clipboard</strong> and select <strong>Mail</strong><strong> </strong>and save the generated email as a draft for safe keeping. click <strong>Done </strong>when you finish this step.</li>
                        <li style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;Margin-bottom:15px;color:#333333;">Click the <strong>Gear</strong> in the <strong>top right corner</strong> of the app and select <strong>Add Issuer</strong>.</li>
                        <li style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;Margin-bottom:15px;color:#333333;">Enter the <strong>Issuer URL</strong> and <strong>one-time code</strong> provided in this email in the fields on the screen. When done, click <strong>Add Issuer</strong>.<br><br><strong>Note</strong>: If you have already used this one-time code, you will need to contact the <strong>Issuer</strong> for a new code.</li>
                        <li style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-size:14px;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;Margin-bottom:15px;color:#333333;">Success! 😀 Your Blockcerts app is now activated and ready to receive badges!<br><br>Instructions with images can be found <a target="_blank" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;font-size:14px;text-decoration:underline;color:#1376C8;" href="https://s3-us-west-2.amazonaws.com/fs.blockcert.poc/images/Steps">here</a>!</li>
                       </ol> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table> </td>
             </tr>
             <tr class="es-mobile-hidden" style="border-collapse:collapse;">
              <td style="Margin:0;padding-top:15px;padding-bottom:20px;padding-left:20px;padding-right:20px;background-position:left top;background-color:#D0CCCC;" bgcolor="#d0cccc" align="left">
               <table width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;">
                 <tr style="border-collapse:collapse;">
                  <td width="560" align="left" style="padding:0;Margin:0;">
                   <table style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-position:left top;" width="100%" cellspacing="0" cellpadding="0">
                     <tr style="border-collapse:collapse;">
                      <td align="left" style="padding:0;Margin:0;"> <br> </td>
                     </tr>
                   </table> </td>
                 </tr>
               </table> </td>
             </tr>
           </table> </td>
         </tr>
       </table> </td>
     </tr>
   </table>
  </div>
 </body>
</html>"""
    
    index = 50
    for recipient in event['inviteRecipients'][:index]:
        nonce = getNonce()
        data = {
            "id": nonce,
            "recipient_email": recipient['email'],
            "issuer_id": event['issuerID'],
            "badges": recipient['badges']
        }
        tableInvites.put_item(Item=data)
        
        you = recipient['email']
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Fresno State uBadges Invitation"
        msg['From'] = me
        msg['To'] = you

        html = htmlTemplate.format(link, nonce)
        part2 = MIMEText(html, 'html') 

        msg.attach(part2)
        try:
            mail.sendmail(me, you, msg.as_string())
        except Exception as e:
            mail.quit()
            test.put_item(Item={'id':str(nonce), 'email':recipient['email']})
            return {"status": "ERROR"}
    mail.quit()
    
    if index >= len(event['inviteRecipients']):
        return {"status": "SUCCEEDED"}
    else:
        return {
            "status": "RUNNING",
            "issuerID": event['issuerID'],
            "inviteRecipients": event['inviteRecipients'][index:]
        }