
# This script is used to launch the application on Windows.

param(
    [string]$Environment = "prod"
)

$pythonPath = ".\venv\Scripts\python.exe"

if ($Environment -eq "dev") {
    $env:APP_DEBUG='true'
    $EnvironmentName = "Development"
} else {
    $env:APP_DEBUG='false'
    $EnvironmentName = "Production"
}

Write-Host "Running application for Environment: $EnvironmentName"

$env:APP_ECHO='false'
$env:APP_DATABASE='euromedia'

.\venv\Scripts\Activate.ps1

git pull

Copy-Item -Path "error.log" -Destination "last_error.log" -Force

Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log"  -NoNewWindow -Wait


