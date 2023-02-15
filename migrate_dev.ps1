


# update_all_databases.ps1
$env:APP_DEBUG='TRUE'

$company_databases = @('euromedia', 'capital', 'mobify', 'realstate')
foreach ($database in $company_databases) {
    Write-Host "Updating database $database..."
    # set the environment variables
    $env:APP_DATABASE=$database
    # run the migration
    alembic upgrade head
}
