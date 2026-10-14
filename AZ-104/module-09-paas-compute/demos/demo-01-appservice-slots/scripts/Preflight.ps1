$ErrorActionPreference = 'Stop'
if (-not (Get-Command az -ErrorAction SilentlyContinue)) { throw 'Instalá Azure CLI y abrí una terminal nueva.' }
$Subscription = (azd env get-value AZURE_SUBSCRIPTION_ID).Trim()
if ($LASTEXITCODE -ne 0 -or -not $Subscription) { throw 'Seleccioná la suscripción de azd antes de continuar.' }
az account show --subscription $Subscription --output none
if ($LASTEXITCODE -ne 0) { throw 'Ejecutá az login con acceso a la suscripción seleccionada.' }
$Runtimes = az webapp list-runtimes --os linux --output tsv
if ($LASTEXITCODE -ne 0 -or ($Runtimes -join ' ') -notmatch 'NODE[:|]22-lts') { throw 'No se pudo confirmar NODE 22-lts. Revisá az webapp list-runtimes --os linux.' }
Write-Host 'Preflight correcto. El laboratorio requiere cuota de App Service Standard S1.'
