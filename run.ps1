
# This script is used to launch the application on Windows.

$pythonPath = ".\venv\Scripts\python.exe"

$env:APP_DEBUG='false'
$env:APP_ECHO='false'
$env:APP_DATABASE='euromedia'

.\venv\Scripts\Activate.ps1

git pull

# Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log" -Append -NoNewWindow -Wait


Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log" -NoNewWindow -Wait | Out-File -FilePath ".\error.log" -Append


