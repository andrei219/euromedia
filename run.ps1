
# This script is used to launch the application on Windows.

$pythonPath = ".\venv\Scripts\python.exe"

$env:APP_DEBUG='false'
$env:APP_ECHO='false'

.\venv\Scripts\Activate.ps1

git pull

Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log" -NoNewWindow -Wait

