#!/bin/bash
sh alert_compass_app-init.sh

###############################################
###############################################
###############################################
bash_isProductionEnvironment=true;
bash_mysql_database="genoa_security";

where_timestamp=$(date +"%Y-%m-%d %H:%M:00%z" --date='5 minutes ago');

bash_mysql_fields=('app_id' 'app_name' 'app_environment' 'app_creation_date' 'entity_id' 'entity_name' 'entity_acronym' 'developer_id' 'developer_username');

bash_mysql_query_name="NULL";

bash_timestamp=$(date +"%Y%m%d_%H%M" --date='5 minutes ago');

bash_is_api_market=true;

#
##
## PREPARING DATA FOR PRO ENVIRONMENT
##

bash_mysql_query_select='SELECT application.app_id as app_id, application.name as app_name,	application.environment as app_environment,	application.creation_date as app_creation_date,	application.entity_id as entity_id,	entity.name as entity_name,	entity.acronym as entity_acronym, developer.id as developer_id,	developer.username as developer_username '
bash_mysql_query_from='FROM genoa_security.application as application, genoa.entity as entity, genoa_security.developer as developer '
bash_mysql_query_where='WHERE entity.id=application.entity_id AND entity.name="compass" AND developer.id=application.developer_id '
bash_mysql_query_filters=" AND application.creation_date > '$where_timestamp';"

bash_mysql_query=$bash_mysql_query_select$bash_mysql_query_from$bash_mysql_query_where$bash_mysql_query_filters

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

pathfile=$(php alert_compass_app-query.php "bash_is_api_market=$bash_is_api_market&bash_timestamp=$bash_timestamp&bash_isProductionEnvironment=$bash_isProductionEnvironment&bash_mysql_query=$bash_mysql_query&bash_mysql_query_name=$bash_mysql_query_name&bash_mysql_database=$bash_mysql_database&bash_mysql_fields=${bash_mysql_fields[*]}")

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
	python alert_compass_app-process_file.py PRO $pathfile
else
	echo '404'
#	exit 0
fi


echo "DONE PRO"
echo "..................................................................................."

