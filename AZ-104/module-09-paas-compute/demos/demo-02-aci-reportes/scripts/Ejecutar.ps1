$ErrorActionPreference = 'Stop'
function EnvValue($Key) {
    $Value = azd env get-value $Key
    if ($LASTEXITCODE -ne 0 -or -not $Value) { throw "No existe $Key en azd." }
    return ($Value -join '').Trim()
}
$Subscription = EnvValue 'AZURE_SUBSCRIPTION_ID'
$Rg = EnvValue 'AZURE_RESOURCE_GROUP'
$Name = EnvValue 'CONTAINER_GROUP_NAME'
az container start --subscription $Subscription --resource-group $Rg --name $Name
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar el trabajo. Revisar eventos del contenedor.' }
Write-Host 'Inicio solicitado. Esperar aproximadamente un minuto y ejecutar .\scripts\Verificar.ps1.'
