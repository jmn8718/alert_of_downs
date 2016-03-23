from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import csv
import sys
import ConfigParser
import os
from datetime import datetime
import time

def toCsv(filename, fieldnames, query, line_delimiter):
  "This method writes the query content in a file"
  with open(filename, 'wb') as csvfile:
    row_writer = csv.writer(csvfile, delimiter=line_delimiter,
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    row_writer.writerow([field for field in fieldnames])
    for row in query:
      row_writer.writerow([field for field in row])

def query_cassandra(cassandra_ip, cassandra_port, cassandra_user, cassandra_password, keyspace, query):
	auth_provider = PlainTextAuthProvider(
        username=cassandra_user, password=cassandra_password)

	cluster = Cluster([cassandra_ip,],port=cassandra_port,auth_provider=auth_provider)
	
	session = cluster.connect()
	#session.execute("CREATE KEYSPACE IF NOT EXISTS "+keyspace+" WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 3};")
	session.execute("USE "+keyspace+";")
	session.set_keyspace(keyspace)

	result = session.execute(query)

	cluster.shutdown()

	return result

def parse_bash_args(argv):
	arguments = {}
	for argv_value in argv.split("&"):
		values = argv_value.split("=")
		arguments[values[0]] = values[1]
	return arguments

# PROCESS THE TIME_PATTERN TO CONVERT PHP TIME_PATTERN TO PYTHON TIME_PATTERN
def parse_time_pattern(time_pattern):
	parsed_timepattern = ''
	if(time_pattern.find('%') == -1):
		for char in time_pattern:
			temp_char = char
			if char.isalpha():
				if char=='i':
					char='M'
				temp_char = '%'+char
			parsed_timepattern += temp_char
	else:
		parsed_timepattern = time_pattern		
	return parsed_timepattern



def main(argv):
	full_filename = ''	
	try:
		bash_arguments = parse_bash_args(argv[0])
		properties = ConfigParser.ConfigParser()

		if(bash_arguments['bash_is_api_market']=='true'):
			properties.read('am_properties.ini')
		else:
			properties.read('properties.ini')

		filename_path = ''
		filetime = ''
		query_name = bash_arguments['bash_mysql_query_name'].replace("NULL", "").lstrip().rstrip()

		if(bash_arguments['bash_timestamp']):
			#print('we have bash')
			filetime = bash_arguments['bash_timestamp']
		else:
			#print('we dont have bash')
			timezone = properties.get('generals','general.timezone')	
			time_pattern = parse_time_pattern(properties.get('generals','general.time.file.pattern'))
			os.environ['TZ'] = timezone
			time.tzset()
			filetime = time.strftime(time_pattern)

		cassandra_port = ''
		cassandra_ip = ''
		cassandra_user = ''
		cassandra_password = ''

		file_delimiter = properties.get('generals','general.file.separator').replace('"','')

		if(bash_arguments['bash_isProductionEnvironment'] == "true"):
			filename_path = properties.get('environment_production','pro.file.folder.alertofdown')
			cassandra_port = properties.get('environment_production','pro.cassandra.port')
			cassandra_ip = properties.get('environment_production','pro.cassandra.ip')
			cassandra_user = properties.get('environment_production','pro.cassandra.user')
			cassandra_password = properties.get('environment_production','pro.cassandra.password')
		else:
			filename_path = properties.get('environment_develop','dev.file.folder.alertofdown')
			cassandra_port = properties.get('environment_develop','dev.cassandra.port')
			cassandra_ip = properties.get('environment_develop','dev.cassandra.ip')
			cassandra_user = properties.get('environment_develop','dev.cassandra.user')
			cassandra_password = properties.get('environment_develop','dev.cassandra.password')

		filename = properties.get('generals','general.file.alertofdown')
		full_filename = filename_path + filetime + '_' + query_name + filename + '.csv'
		
		###
		# GENERATE THE QUERY WITH THE BASH PARAMS
		###
		query_fieldnames = bash_arguments['bash_mysql_fields'].split(' ')
		query_fieldname_string = ', '.join(query_fieldnames)
		query = 'SELECT '+query_fieldname_string+' FROM '+bash_arguments['bash_mysql_database']+'.'+bash_arguments['bash_mysql_table'] + ' '+bash_arguments['bash_mysql_where']
		#print query

		query_result = query_cassandra(cassandra_ip, cassandra_port, cassandra_user, cassandra_password, bash_arguments['bash_mysql_database'],query)
		toCsv(full_filename, query_fieldnames, query_result, file_delimiter)

	except:
		print("Unexpected error:" + str(sys.exc_info()))
		sys.exit("Unexpected error:" + str(sys.exc_info()))

	if len(full_filename) > 0:
		print(full_filename)
		sys.exit(1)
	else:
		sys.exit(0)  

main(sys.argv[1:])