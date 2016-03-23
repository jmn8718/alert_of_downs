import sys
from mailing import alert_compass_app_mailing

def groupApps(headers, appsList):
	apps = []
	headers = headers.replace('\n','').split(';')
	index_developer_username = -1
	index_app_name = -1
	index_app_environment = -1
	for x in range(0,len(headers)):
		if(headers[x]=='developer_username'):
			index_developer_username = x
		elif(headers[x]=='app_name'):
			index_app_name = x
		elif(headers[x]=='app_environment'):
			index_app_environment = x
	for app in appsList:
		app = app.replace('\n','').split(';')
		apps.append({'app_name': app[index_app_name],
					'developer_username': app[index_developer_username],
					'environment':app[index_app_environment]})

	return apps

def toMailing(headers, appsList):
	apps = groupApps(headers, appsList)
	for app in apps:
		#print(str(app))
		alert_compass_app_mailing(app['environment'],app['app_name'],app['developer_username'])

def fileToMail(environment,filename):
	data=''
	with open (filename, "r") as myfile:
	    data=myfile.readlines()
	if(len(data)>1):
		toMailing(data[0],data[1:])

def main(argv):
	#argv[0] must be the environment ["DEV","QA","PRE","PRO"]
	print('Lets process the file "'+argv[1]+'" in the environment "'+argv[0]+'"')
	fileToMail(argv[0],argv[1])
	print('Done processing the file "'+argv[1]+'" in the environment "'+argv[0]+'"')
	sys.exit(1)

main(sys.argv[1:])
