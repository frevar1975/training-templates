$ErrorActionPreference = 'Stop'
function EnvValue($Key) {
    $Value = azd env get-value $Key
    if ($LASTEXITCODE -ne 0 -or -not $Value) { throw "No existe $Key en azd." }
    return ($Value -join '').Trim()
}
$Sub = EnvValue 'AZURE_SUBSCRIPTION_ID'
$Rg = EnvValue 'AZURE_RESOURCE_GROUP'
$Name = EnvValue 'CONTAINER_APP_NAME'
$Raw = az containerapp show --subscription $Sub -g $Rg -n $Name --output json
if ($LASTEXITCODE -ne 0) { throw 'No se pudo consultar la app.' }
$App = ($Raw -join "`n") | ConvertFrom-Json
Write-Host 'App:' $Name
Write-Host 'Aprovisionamiento:' $App.properties.provisioningState
Write-Host 'Minimo:' $App.properties.template.scale.minReplicas 'Maximo:' $App.properties.template.scale.maxReplicas
Write-Host 'Reglas:' ($App.properties.template.scale.rules | ConvertTo-Json -Depth 8 -Compress)
$Revision = $App.properties.latestReadyRevisionName
if (-not $Revision) { throw 'No hay una revision lista. Revisar eventos y logs.' }
az containerapp replica list --subscription $Sub -g $Rg -n $Name --revision $Revision --output json
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron consultar replicas.' }
Write-Host 'Una lista [] indica que esa revision no tiene replicas en ese momento.'
Write-Host 'Esta consulta usa el plano de administracion; no envia solicitudes HTTP a la tienda.'
