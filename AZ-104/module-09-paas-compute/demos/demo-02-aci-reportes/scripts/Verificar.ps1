$ErrorActionPreference = 'Stop'
function EnvValue($Key) {
    $Value = azd env get-value $Key
    if ($LASTEXITCODE -ne 0 -or -not $Value) { throw "No existe $Key en azd." }
    return ($Value -join '').Trim()
}
$Subscription = EnvValue 'AZURE_SUBSCRIPTION_ID'
$Rg = EnvValue 'AZURE_RESOURCE_GROUP'
$Name = EnvValue 'CONTAINER_GROUP_NAME'
az container show --subscription $Subscription --resource-group $Rg --name $Name --query "containers[].{Nombre:name,Estado:instanceView.currentState.state,Salida:instanceView.currentState.exitCode,Inicio:instanceView.currentState.startTime,Fin:instanceView.currentState.finishTime}" --output table
if ($LASTEXITCODE -ne 0) { throw 'No se pudo consultar el estado.' }
az container logs --subscription $Subscription --resource-group $Rg --name $Name --container-name generador
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron consultar los logs.' }
Write-Host 'Cuenta de Storage:' (EnvValue 'STORAGE_ACCOUNT_NAME')
Write-Host 'Recurso compartido: reportes. Abrilo desde File shares en el portal.'
