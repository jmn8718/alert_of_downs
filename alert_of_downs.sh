#!/bin/bash
sh alert_of_downs-init.sh

###############################################
###############################################
###############################################
bash_isProductionEnvironment=false;
bash_mysql_database="genoa_statistics";
bash_mysql_table="statistics_entity_calls_code_counter";

where_timestamp=$(date +"%Y-%m-%d %H:%M:00%z" --date='10 minutes ago');
#Starts with " WHERE ". NOTE: To don't use set "NULL"
bash_mysql_where="WHERE interval_dt_tm > '$where_timestamp' ALLOW FILTERING";

#Must end with "_". NOTE: To don't use set "NULL"
bash_mysql_query_name="NULL";

#Format ("field1" "field2" "field3")
bash_mysql_fields=('entity_id' 'interval_dt_tm' 'api_environment' 'api_name' 'api_version' 'resource_name' 'counter' 'response_status_code');

bash_timestamp=$(date +"%Y%m%d_%H%M" --date='10 minutes ago');

bash_is_api_market=true;

echo "..................................................................................."
echo "PROCESSING DEV ENVIRONMENT"
echo $(date +"%Y%m%d_%H%M")

echo "=================="
echo "1.- Environment : $bash_isProductionEnvironment"
echo "2.- Database : $bash_mysql_database"
echo "3.- Table : $bash_mysql_table"
echo "4.- Where sentence : $bash_mysql_where"
echo "5.- Query name : $bash_mysql_query_name"
echo "6.- Fields : ${bash_mysql_fields[*]}"
echo "7.- Is API_Market : $bash_is_api_market"
echo "8.- Timestamp : $bash_timestamp"
echo "=================="
echo "Lets query the cassandra db"
echo "=================="

pathfile=$(python alert_of_downs-query.py "bash_is_api_market=$bash_is_api_market&bash_timestamp=$bash_timestamp&bash_isProductionEnvironment=$bash_isProductionEnvironment&bash_mysql_database=$bash_mysql_database&bash_mysql_table=$bash_mysql_table&bash_mysql_where=$bash_mysql_where&bash_mysql_query_name=$bash_mysql_query_name&bash_mysql_fields=${bash_mysql_fields[*]}")

echo "=================="
echo "PYTHON RETURN:"
echo $pathfile
echo "=================="
if [[ "$pathfile" == *"Unexpected error"* ]]
then 
	echo 'error in the process of query cassandra'
#	exit 0
elif [ -n "$pathfile" ]
then	
	echo 'Success querying cassandra'
#	#cat $pathfile
	python alert_of_downs-process_file.py DEV $pathfile
else
	echo '404'
#	exit 0
fi


echo "DONE DEV"
echo "..................................................................................."

sleep 10
##
## PREPARING DATA FOR PRO ENVIRONMENT
##

bash_mysql_query_select='SELECT monitoring.entity_id, monitoring.creation_date as interval_dt_tm, apienvironment.environment as api_environment, apidata.name as api_name, apiversion.version as api_version, monitoring.service as resource_name, monitoring.counter as counter, monitoring.response_code as response_status_code '
bash_mysql_query_where='WHERE monitoring.api=apidata.name AND monitoring.entity_id=apidata.entity_id AND apidata.id=apiversion.api_id AND apiversion.id=apienvironment.api_version_id '
bash_mysql_query_from='FROM genoa_monitoring.developer_AppApiServ as monitoring, genoa.api as apidata, genoa.api_version as apiversion, genoa.api_version_environment as apienvironment '
#bash_mysql_query_filters=" AND monitoring.creation_date > '$where_timestamp' AND monitoring.response_code >= 500 ORDER BY monitoring.creation_date DESC;"
bash_mysql_query_filters=" AND monitoring.creation_date > '$where_timestamp' ORDER BY monitoring.creation_date DESC;"

bash_mysql_query=$bash_mysql_query_select$bash_mysql_query_from$bash_mysql_query_where$bash_mysql_query_filters

bash_isProductionEnvironment=true;
bash_mysql_database="genoa_monitoring";

echo "..................................................................................."
echo "PROCESSING PRO ENVIRONMENT"
echo $(date +"%Y%m%d_%H%M")

echo "=================="
echo "1.- Environment : $bash_isProductionEnvironment"
echo "2.- Database : $bash_mysql_database"
echo "3.- Query : $bash_mysql_query"
echo "5.- Query name : $bash_mysql_query_name"
echo "6.- Fields : ${bash_mysql_fields[*]}"
echo "7.- Is API_Market : $bash_is_api_market"
echo "8.- Timestamp : $bash_timestamp"
echo "=================="
echo "Lets query the mysql db"
echo "=================="

pathfile=$(php alert_of_downs-query.php "bash_is_api_market=$bash_is_api_market&bash_timestamp=$bash_timestamp&bash_isProductionEnvironment=$bash_isProductionEnvironment&bash_mysql_query=$bash_mysql_query&bash_mysql_query_name=$bash_mysql_query_name&bash_mysql_database=$bash_mysql_database&bash_mysql_fields=${bash_mysql_fields[*]}")

echo "=================="
echo "PHP RETURN:"
echo $pathfile
echo "=================="
if [[ "$pathfile" == *"Unexpected error"* ]]
then 
	echo 'error in the process of query mysql'
#	exit 0
elif [ "$pathfile" == "0" ]
then	
	echo 'No records saved'
elif [ -n "$pathfile" ]
then	
	echo 'Success querying mysql'
	#cat $pathfile
	python alert_of_downs-process_file.py PRO $pathfile
else
	echo '404'
#	exit 0
fi


echo "DONE PRO"
echo "..................................................................................."