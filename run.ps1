
# This script is used to launch the application on Windows.

$pythonPath = ".\venv\Scripts\python.exe"

$env:APP_DEBUG='false'
$env:APP_ECHO='false'
$env:APP_DATABASE='euromedia'

.\venv\Scripts\Activate.ps1

git pull

Copy-Item -Path "error.log" -Destination "last_error.log" -Force

Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log"  -NoNewWindow -Wait

# venv\Scripts\python.exe .\app\checkgit.py


#Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log" -NoNewWindow -Wait | Out-File -FilePath ".\error.log" -Append


