<?php

function toCsv($file, $fields, $content , $field_separator){
	$fp = fopen($file, "w");
	$count_writes = 0;
    fputs($fp, implode($fields, $field_separator) . "\n");
	if ($content->num_rows > 0) {

		#echo 'The file has '.$content->num_rows.' records' . PHP_EOL;
		mysqli_data_seek($content, 0);
	    while ($row = mysqli_fetch_array($content, MYSQLI_BOTH)) {
	        $row_array = Array();
	        foreach ($fields as $field_name) {
	            $row_array[$field_name] = $row[$field_name];
	        }
	        $row_array = str_replace('"', '', $row_array);
	        fputs($fp, implode($row_array, $field_separator) . "\n");
	        $count_writes++;
	    }
	} else {
		#echo 'The file has 0 records' . PHP_EOL;
	}

	fclose($fp);

#	echo PHP_EOL . "Created file: " . $file . PHP_EOL;
	return $content->num_rows;
}
function queryMysql($database, $query, $environment){
	$properties = parse_ini_file('am_properties.ini', true);

	if ($environment=="true") {
		$mysql_url = $properties["environment_production"]["pro.mysql.url"];
	    $mysql_port = $properties["environment_production"]["pro.mysql.port"];
	    $mysql_user = $properties["environment_production"]["pro.mysql.user"];
	    $mysql_pass = $properties["environment_production"]["pro.mysql.pass"];
	    $mysql_certificate = $properties["environment_production"]["pro.mysql.certificate"];
	} else {
		$mysql_url = $properties["environment_develop"]["dev.mysql.url"];
	    $mysql_port = $properties["environment_develop"]["dev.mysql.port"];
	    $mysql_user = $properties["environment_develop"]["dev.mysql.user"];
	    $mysql_pass = $properties["environment_develop"]["dev.mysql.pass"];
	    $mysql_certificate = $properties["environment_develop"]["dev.mysql.certificate"];
	}
	/******************************************/
	/******************************************/
	/* Getting the Data from DATABASE */
	/******************************************/
	/******************************************/
#	echo "------------------------------".PHP_EOL;
#	echo "Stablising DB conection to ".$environment;
#	echo PHP_EOL."------------------------------".PHP_EOL;
#	echo "Username: " . $mysql_user.PHP_EOL;
#	echo "URL: " . $mysql_url.PHP_EOL;
#	echo "Port: " . $mysql_port.PHP_EOL;
#	echo "Query: " . $query.PHP_EOL;

	$mysqli = mysqli_init();
	if (!$mysqli) {
	    echo "Unexpected error in mysqlinit";
	    die("\nMysqli_init fail");
	} else {
	    #echo "\nDataBase initialized";
	}
	if ($environment=="true") {
#	    echo "\nSetting Pro Environment DataBase parameters...";
	    mysqli_options($mysqli, MYSQLI_OPT_SSL_VERIFY_SERVER_CERT, true);
	    mysqli_ssl_set($mysqli, NULL, NULL, $mysql_certificate, NULL, NULL);
	}

	$mysqli_connection = mysqli_real_connect($mysqli, $mysql_url, $mysql_user, $mysql_pass, $database, $mysql_port, NULL, NULL);

	if (mysqli_connect_errno()) {
	    echo "Unexpected error in mysql connection";
	    die("\nFailed to connect to MySQL: " . mysqli_connect_error());
	}

#	echo PHP_EOL. PHP_EOL ."Conected".PHP_EOL;

#	echo PHP_EOL."SQL generated: " . $query . PHP_EOL;

	$result = $mysqli->query($query);
#	echo PHP_EOL."Number of records: #" . $result->num_rows . PHP_EOL;

	#var_dump($result);

	$mysqli->close();

	return $result;
}

parse_str($argv[1]);

$bash_mysql_query = ($bash_mysql_query=="NULL") ? " " : $bash_mysql_query;
$bash_mysql_query_name = ($bash_mysql_query_name=="NULL") ? " " : $bash_mysql_query_name;
$bash_mysql_fields = explode(" ", $bash_mysql_fields);
$bash_timestamp = $bash_timestamp;


$filetime = $bash_timestamp or die("bash_timestamp - Unexpected error\n");
$isProductionEnvironment = $bash_isProductionEnvironment or die("bash_isProductionEnvironment - Unexpected error\n");

$mysql_database = $bash_mysql_database or die("bash_mysql_database - Unexpected error\n");
$mysql_query_name = $bash_mysql_query_name or die("bash_mysql_query_name - Unexpected error\n");
$mysql_query = $bash_mysql_query or die("bash_mysql_query - Unexpected error\n");
$mysql_fields = $bash_mysql_fields or die("bash_mysql_fields - Unexpected error\n");

$properties = parse_ini_file('am_properties.ini', true);

if ($bash_isProductionEnvironment=="true") {
    $filename_path = $properties["environment_production"]["pro.file.folder.alertcompassapp"];
} else {
    $filename_path = $properties["environment_develop"]["dev.file.folder.alertcompassapp"];
}
$filename =  $properties["generals"]["general.file.alertcompassapp"];

$full_filename = $filename_path . $filetime . '_' . $filename . '.csv';

$field_delimiter = $properties["generals"]["general.file.separator"];

$query_result = queryMysql($mysql_database, $mysql_query, $bash_isProductionEnvironment);

$records_saved = toCsv($full_filename,$mysql_fields, $query_result, $field_delimiter);

if($records_saved>0){
	echo $full_filename;
} else {
	echo 0;
}

?>