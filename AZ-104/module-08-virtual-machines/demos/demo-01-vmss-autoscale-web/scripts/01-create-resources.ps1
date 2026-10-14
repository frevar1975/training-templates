param(
    [Parameter(Mandatory=$true)][string]$SubscriptionId,
    [string]$Environment='az104-m08-vmss',
    [string]$Location='eastus2',
    [string]$VmSize='Standard_D2s_v5'
)
$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
function Check-Azd { if ($LASTEXITCODE -ne 0) { throw 'azd falló. Resuelve el error antes de continuar.' } }
# Ejecuta azd auth login antes de llamar a este script.
azd env select $Environment 2>$null
if ($LASTEXITCODE -ne 0) { azd env new $Environment; Check-Azd }
azd env set AZURE_SUBSCRIPTION_ID $SubscriptionId
Check-Azd
azd env set AZURE_LOCATION $Location
Check-Azd
azd env set VM_SIZE $VmSize
Check-Azd
& (Join-Path $PSScriptRoot 'Preparar-Clave.ps1')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar la clave pública.' }
azd up
Check-Azd
& (Join-Path $PSScriptRoot 'Obtener-Url.ps1')
