SELECT application.app_id as app_id, 
	application.name as app_name, 
	application.environment as app_environment,
	application.creation_date as app_creation_date,
	application.entity_id as entity_id,
	entity.name as entity_name,
	entity.acronym as entity_acronym,
	developer.id as developer_id,
	developer.username as developer_username
FROM genoa_security.application as application, 
	genoa.entity as entity,
	genoa_security.developer as developer
WHERE entity.id=application.entity_id AND
	entity.name="compass" AND 
	developer.id=application.developer_id;