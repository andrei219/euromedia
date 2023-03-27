

# Receives a branch parameter and re-creates and dumps database for that branch
# This script will dump the production databases and import them into the development environment

param (
    [string]$Branch = ""
)

if ($Branch.Trim() -eq "") {
    Write-Host "Usage: CreateBranchDBs.ps1 -Branch <branch_name>"
    exit
}

Write-Host "Running migration for Branch: $Branch"

$branch_databases = @(
    "euromedia_$Branch",
    "capital_$Branch",
    "mobify_$Branch",
    "realstate_$Branch"
)

foreach ($db in $branch_databases){
    Write-Host "Recreating database $db..."
    mysql --execute "DROP DATABASE IF EXISTS $db; CREATE DATABASE $db" --user=root --password=hnq#4506 --host=localhost
    mysqldump --user=root --password=hnq#4506 --host=localhost "$($db.Replace("_$Branch", ''))" | mysql --user=root --password=hnq#4506 --host=localhost "$db"
    write-host "---------------------------------------------------"
}


