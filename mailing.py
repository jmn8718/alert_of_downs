from __future__ import print_function

from apiclient import discovery
from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from httplib2 import Http

import os, sys

from lib_email import CreateMessage,SendMessage 
from slackclient import SlackClient
import time
import json

#try:
#    import argparse
#    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#except ImportError:
#    flags = None

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = '.credentials/client_secret.json'
APPLICATION_NAME = 'mailins_error_status'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    filepath = os.path.dirname(os.path.abspath(__file__))
    #home_dir = os.path.expanduser('~')
    #credential_dir = os.path.join(home_dir, '.credentials')
    credential_dir = os.path.join(filepath ,'.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'accepted_credentials.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_service():
	credentials = get_credentials()
	http_auth = credentials.authorize(Http())
	service = discovery.build('gmail', 'v1', http=http_auth)
	return service

EMAIL_TEMPLATE = '<img style="display: block;margin: 0 auto 15px;" src="https://ci3.googleusercontent.com/proxy/Z5nXsjoLJBrwDddvAwaw071OB8oe8fLQhF6tYAEukiy2zeYv5glpzotvy6Lz3fAoU_WSSrcVmPDHMu2H2qChrhNYbpnV-0lpB_lE_Ax12nPXV_WEcUFSnsJb56iS4s6bcbaJ1Kvp=s0-d-e1-ft#https://www.bbvaapimarket.com/bbva-amazing-theme/images/api-market-alfa-logo.png"><br>'
def templateMessage(environment, entity, api, errors):
	message = '<table style="text-align:center;font-family:Arial,Helvetica,Verdana,Trebuchet,Tahoma,Futura;font-size:20px;line-height:28px" cellpadding="0" cellspacing="0" width="100%"><tbody><tr><td><table style="max-width:620px;width:100%" border="0" cellpadding="0" cellspacing="0" align="center">                <tbody><tr><td width="10" bgcolor="#fff">&nbsp;</td><td><table style="width:100%;max-width:600px" border="0" cellpadding="0" cellspacing="0" bgcolor="#ffffff"><tbody><tr><td colspan="3" style="line-height:0;padding:40px 0 20px 0" align="center"><img class="CToWUd" src="https://www.bbvaapimarket.com/bbva-amazing-theme/images/api-market-alfa-logo.png"></td></tr>                            <tr><td colspan="3" style="height:30px;background-color:#006ec1" align="center"></td></tr><tr><td colspan="3" style="font-family:Arial,Helvetica,sans-serif;padding:40px 40px 0 40px;margin:0" align="left"><h1 style="margin:0;line-height:26px;display:block;font-size:20px;font-weight:normal;color:#006ec1;text-align:center;text-transform:uppercase">                                        <strong style="font-weight:normal">API_MARKET - </strong>API_Market - APIs Status Notification</h1></td></tr><tr><td colspan="3" style="font-family:Arial,Helvetica,sans-serif;color:#566270;font-size:15px;line-height:19px;padding:30px 40px" align="left">'
	message += '<h1><h1 style="margin:0;line-height:26px;display:block;font-size:20px;font-weight:normal;color:#006ec1;text-align:center;text-transform:uppercase">In the environment '+environment+'</h1>'
	message += '<p>The api "'+api+'" in the entity "'+entity+'" has the following errors in the last 10 minutes:</p>'
	message += '<ul>'
	for error in errors:
		message += '<li>The service '+error['service']+' has the code: <strong>'+error['response_code']+'</strong><br> '+error['counter']+' times in the period of '+error['timestamp']+'</li>'
	message += '</ul>'
	message +='</td></tr>    <tr><td colspan="3" style="height:50px;background-color:#006ec1" align="center"></td></tr>    <tr>        <td colspan="3" style="line-height:0;padding:20px 0" align="center">            <img class="CToWUd" src="https://www.bbvaapimarket.com/documents/10197/26970/image_logo_BBVA/785cd1ae-5f8d-46fc-a738-734047f999ed?t=1456920665347">        </td></tr>    </tbody></table></td></tr></tbody></table></td></tr></tbody></table>'
	return message

def sendSlack(channel, message, username, icon_emoji):
	try:
		token = 'Add token here'
		sc = SlackClient(token)
		result_bot = sc.api_call(
		    "chat.postMessage", channel=channel, text=message,
		    username=username, icon_emoji=icon_emoji
		)
		if(result_bot['ok']==True):
			print('Slack ok')
		else:
			raise Exception('Error in slack '+str(result_bot))
	except:
		print("Unexpected error in sendSlack:" + str(sys.exc_info()))

def sendMail(subject, to,message):
	try:
		service = get_service()
		if service:
			sender = 'add sender here'
			to = to
			message_text = message
			message = CreateMessage(sender,to, subject, message_text)
			result = SendMessage(service, 'me', message)
			print(result)
			print('mail ok')
		else:
			raise Exception('No service')
	except:
		print("Unexpected error:" + str(sys.exc_info()))

def id_to_entity_name(environment, entity_id):
	myEntity = ''
	if(environment=='DEV'):
		if(entity_id=='60'):
			myEntity='bbva'
		elif(entity_id=='61'):
			myEntity='compass'
		elif(entity_id=='1'):
			myEntity='default'
		else:
			myEntity='entity__'+environment+'-'+str(entity_id)
	elif(environment=='PRO'):
		if(entity_id=='6'):
			myEntity='bbva'
		elif(entity_id=='13'):
			myEntity='compass'
		else:
			myEntity='entity__'+environment+'-'+str(entity_id)
	else:
		myEntity = 'noenv__'+str(entity_id)
	return myEntity

def get_receiver(entity, api):
	receiver = ''
	myApi = api.lower()
	if('bbva'==entity):
		if('identity' in myApi or 'accounts' in myApi or 'cards' in myApi or 'money-transfers' in myApi):
			receiver = ', add another email'
		elif('paystats' in myApi):
			receiver = ', add another email'
	elif('compass'==entity):
		myApi = api.lower()
		if('accounts' in myApi):
			receiver = ''#', compass'
	return receiver

def alert_of_down_mailing(environment, entity, api, errors):	
	to = 'add email'

	myEntity = id_to_entity_name(environment,entity)
	#TODO add receiver checkig the api
	if( "PRO" in environment):
		to += ', add another email'
		to += get_receiver(myEntity, api)

	message = templateMessage(environment, myEntity, api, errors)
	print('=====================================================')
	print('The api "'+api+'" in the entity "'+myEntity+'" had errors')
	print('Error information to "'+to+'"')
	subject = 'API_Market '+environment+' - API Service Error - API '+api
	print(subject)
	sendMail(subject, to, message)
	print('email was sent')
	print('=====================================================')

	channel = "#api_market_aod_" +environment.lower()
	slackMessage = '===========================================================\n'
	slackMessage += "Errors in api '"+api+"' in the entity '"+myEntity+"' in "+environment+"\n"
	slackMessage += str(errors)
	slackMessage += '===========================================================\n'
	username = 'Error reporter'
	emoji = ':loudspeaker:'

	sendSlack(channel, slackMessage, username, emoji)
	print('email was sent')
	print('=====================================================')

def alert_compass_app_mailing(environment,app,developer):
	to = 'add emails'
	message = 'The developer "'+developer+'" has created the app "'+app+'" in the environment "'+environment+'".'
	subject = 'API_Market Alert - Compass APP creation'
	sendMail(subject, to, message)
	
	channel = "#compass_apps"
	slackMessage = '===========================================================\n'
	slackMessage += 'The developer "'+developer+'" has created the app "'+app+'" in the environment "'+environment+'".\n'
	slackMessage += '===========================================================\n'
	username = 'Compass reporter'
	emoji = ':loudspeaker:'

	sendSlack(channel, slackMessage, username, emoji)

def main():
	sendMail('test@email.com','send')

if __name__ == '__main__':
    main()
