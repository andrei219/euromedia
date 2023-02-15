
# update_all_databases.ps1

param(
    [string]$Environment = "dev",
    [String]$Revision = $null
)

if ($Environment -eq "dev") {
    $env:APP_DEBUG='TRUE'
    $EnvironmentName = "Development"
} else {
    $env:APP_DEBUG='FALSE'
    $EnvironmentName = "Production"
}

Write-Host "Running migration for Environment: $EnvironmentName"

if ($Revision -eq $null) {
    $Revision = "head"
}

Write-Host "Running migration for Revision: $Revision"

$company_databases = @('euromedia', 'capital', 'mobify', 'realstate')
foreach ($database in $company_databases) {
    Write-Host "Updating database $database..."
    # set the environment variables
    $env:APP_DATABASE=$database
    # run the migration
    alembic upgrade $Revision
}

