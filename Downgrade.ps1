

# Downgrade by a number of revisions or give a specific revision to downgrade to

param (
    [string]$Environment = "dev",
    [String]$Revision = "",
    [String]$NumberOfRevisions = ""
)

if ($Environment -eq "dev") {
    $env:APP_DEBUG='TRUE'
    $EnvironmentName = "Development"
} else {
    $env:APP_DEBUG='FALSE'
    $EnvironmentName = "Production"
}

Write-Host "Running migration for Environment: $EnvironmentName"

if ($Revision.Trim() -eq "" -and $NumberOfRevisions.Trim() -eq "") {
    Write-Host "You must specify a revision or a number of revisions to downgrade"
    exit
}

$company_databases = @('euromedia', 'capital', 'mobify', 'realstate')
foreach ($database in $company_databases) {
    Write-Host "Updating database $database..."
    # set the environment variables
    $env:APP_DATABASE=$database
    # run the migration
    if ($Revision.Trim() -ne "") {
        Write-Host "Running migration for Revision: $Revision"
        alembic downgrade $Revision
    } else {
        write-host "Running migration for $NumberOfRevisions revisions"
        alembic downgrade $NumberOfRevisions
    }
}

