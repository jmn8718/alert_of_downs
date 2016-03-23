if [ -d "csv" ]; then
 	echo 'Folder "csv" exists'
else
	mkdir csv
fi

if [ -d "csv/service_status_dev" ]; then
	echo 'Folder "csv/service_status_dev" exists'
else
	mkdir csv/service_status_dev
	echo 'Folder "csv/service_status_dev" created'
fi

if [ -d "csv/service_status_pro" ]; then
	echo 'Folder "csv/service_status_pro" exists'
else
	mkdir csv/service_status_pro
	echo 'Folder "csv/service_status_pro" created'
fi
