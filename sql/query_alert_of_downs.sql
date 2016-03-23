SELECT monitoring.entity_id, 
	monitoring.creation_date as interval_dt_tm,
	apienvironment.environment as api_environment,
	apidata.name as api_name,
	apiversion.version as api_version,
	monitoring.service as resource_name,
	monitoring.counter as counter,
	monitoring.response_code as response_status_code
FROM genoa_monitoring.developer_AppApiServ as monitoring,
	genoa.api as apidata,
	genoa.api_version as apiversion,
	genoa.api_version_environment as apienvironment
WHERE monitoring.api=apidata.name AND
	monitoring.entity_id=apidata.entity_id AND
	apidata.id=apiversion.api_id AND
	apiversion.id=apienvironment.api_version_id AND
	monitoring.response_code>=500
ORDER BY monitoring.creation_date DESC
LIMIT 100;