
Write-Host "`$env:APP_DATABASE=$env:APP_DATABASE"
Write-Host "`$env:APP_DEBUG=$env:APP_DEBUG"
Write-Host "`$env:APP_ECHO=$env:APP_ECHO"
Write-Host "`$env:APP_MAIL_PASSWORD=$env:APP_MAIL_PASSWORD"
Write-Host "`$env:GITHUB_AUTH=$env:GITHUB_AUTH"

Write-Host "Current branch: $(git branch --show-current)"