if [ -d "csv" ]; then
 	echo 'Folder "csv" exists'
else
	mkdir csv
fi

if [ -d "csv/alerts_compass_app_pro" ]; then
	echo 'Folder "csv/alerts_compass_app_pro" exists'
else
	mkdir csv/alerts_compass_app_pro
	echo 'Folder "csv/alerts_compass_app_ro" created'
fi
