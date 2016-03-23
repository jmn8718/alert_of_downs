import sys
from mailing import alert_of_down_mailing

def groupErrors(headers, errorList,minimun_error_code):
	"This method group the errors by api and provider"
	index_api = -1
	index_version = -1
	index_entity = -1
	index_service = -1
	index_response_code = -1
	index_timestamp = -1
	index_count = -1
	index_api_environment = -1
	headers = headers.replace('\n','').split(';')
	mailingData = {}
	for x in range(0,len(headers)):
		if(headers[x]=='api_name'):
			index_api = x
		if(headers[x]=='api_version'):
			index_version = x
		elif(headers[x]=='resource_name'):
			index_service = x
		elif(headers[x]=='entity_id'):
			index_entity = x
		elif(headers[x]=='response_status_code'):
			index_response_code = x
		elif(headers[x]=='interval_dt_tm'):
			index_timestamp = x
		elif(headers[x]=='counter'):
			index_count = x
		elif(headers[x]=='api_environment'):
			index_api_environment = x

	for error in errorList:
		error = error.replace('\n','').split(';')
		if(int(error[index_response_code])>=minimun_error_code):
			#print(error[index_response_code])
			if(error[index_entity] not in mailingData):
				#print 'entity not in'
				mailingData[error[index_entity]]={ 
					error[index_api]: [{ 
						'response_code': error[index_response_code], 
						'service': error[index_service], 
						'timestamp': error[index_timestamp], 
						'counter': error[index_count],
						'environment': error[index_api_environment]
					}] 
				}
			else:
				#print 'entity in'
				if(error[index_api] not in mailingData[error[index_entity]]):
					#print 'api not in'
					mailingData[error[index_entity]][error[index_api]]=[
						{ 	'response_code': error[index_response_code], 
							'service': error[index_service], 
							'timestamp': error[index_timestamp], 
							'counter': error[index_count],
							'environment': error[index_api_environment]
						}
					]
				else:
					#print 'api in'
					mailingData[error[index_entity]][error[index_api]].append({ 
						'response_code': error[index_response_code], 
						'service': error[index_service], 
						'timestamp': error[index_timestamp], 
						'counter': error[index_count],
						'environment': error[index_api_environment]
					})
		#else:
		#	print(error[index_response_code]+' '+error[index_service])
	return mailingData
	
def toMailing(environment, headers, errorList):
	errors = groupErrors(headers, errorList,500)
	for entity in errors:
		for api in errors[entity]:
			alert_of_down_mailing(environment,entity,api,errors[entity][api])

def fileToMail(environment,filename):
	data=''
	with open (filename, "r") as myfile:
	    data=myfile.readlines()
	if(len(data)>1):
		toMailing(environment,data[0],data[1:])

def main(argv):
	#argv[0] must be the environment ["DEV","QA","PRE","PRO"]
	print('Lets process the file "'+argv[1]+'" in the environment "'+argv[0]+'"')
	fileToMail(argv[0],argv[1])
	print('Done processing the file "'+argv[1]+'" in the environment "'+argv[0]+'"')
	sys.exit(1)

main(sys.argv[1:])
