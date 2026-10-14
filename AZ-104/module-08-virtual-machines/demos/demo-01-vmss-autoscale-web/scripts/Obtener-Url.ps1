$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
$Url=azd env get-value DEMO_URL
if ($LASTEXITCODE -ne 0 -or -not $Url) { throw 'No existe DEMO_URL. Completa azd up o ejecuta azd env refresh.' }
$Url=$Url.Trim()
$Url | Set-Content -Encoding ascii (Join-Path $projectRoot 'url-demo.txt')
Write-Host "URL de los alumnos: $Url"
