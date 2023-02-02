
# This script is used to launch the application on Windows.

$pythonPath = ".\venv\Scripts\python.exe"

$env:APP_DEBUG='false'
$env:APP_ECHO='false'

$mail_path = '.\mailunch\bin\Debug\net6.0\mailunch.exe'
$easysii_path = '.\easysii\bin\Debug\net6.0\easysii.exe'

$env:Path = "$env:Path;$mail_path;$easysii_path"


.\venv\Scripts\Activate.ps1

git pull

Start-Process $pythonPath .\app\run.py -RedirectStandardError ".\error.log" -NoNewWindow -Wait


