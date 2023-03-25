
# update_all_databases.ps1

param(
    [string]$Environment = "dev",
    [String]$Revision = "",
    [String]$Branch = ""
)

if ($Environment -eq "dev") {
    $env:APP_DEBUG='TRUE'
    $EnvironmentName = "Development"
} else {
    $env:APP_DEBUG='FALSE'
    $EnvironmentName = "Production"
}

Write-Host "Running migration for Environment: $EnvironmentName"

if ($Revision.Trim() -eq "") {
    $Revision = "head"
}

Write-Host "Running migration for Revision: $Revision"

$company_databases = @('euromedia', 'capital', 'mobify', 'realstate')
foreach ($database in $company_databases) {
    $database = $database + "_$Branch"
    Write-Host "Updating database $database..."
    # set the environment variables
    $env:APP_DATABASE=$database
    # run the migration
    alembic upgrade $Revision
}

# Sets the database to euroemdia
$env:APP_DATABASE='euromedia' + "_$Branch"

# Sets environment to debug mode
$env:APP_DEBUG='TRUE'



