

# This script will dump the production databases and import them into the development environment

$company_databases = @('euromedia', 'capital', 'mobify', 'realstate')

foreach ($database in $company_databases){
    mysql.exe --execute="DROP DATABASE IF EXISTS $database; CREATE DATABASE $database" --user=root --password=hnq#4506 --host=localhost
    Write-Host "Recreated development database $database"
    write-host "---------------------------------------------------"
}

foreach  ($database in $company_databases) {
    Write-Host "Dumping production database $database..."
    # set the environment variables
    $env:APP_DATABASE=$database
    mysqldump.exe --user=andrei --host=192.168.1.78 --password=hnq#4506 "$($env:APP_DATABASE)"`
    | mysql --user=root --password=hnq#4506 --host=localhost "$($env:APP_DATABASE)"
    write-host "---------------------------------------------------"
}