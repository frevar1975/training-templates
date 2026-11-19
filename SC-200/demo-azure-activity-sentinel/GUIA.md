# Laboratorio 1 Investigar Azure Activity en Microsoft Sentinel

## 1 Confirmá la sesión y el destino

**Objetivo.** Seguir un cambio administrativo desde el Registro de actividad de Azure hasta la tabla `AzureActivity` de Sentinel y correlacionar el inicio y el resultado.

**Escenario.** El SOC necesita investigar un cambio de configuración. Identificá la operación, su hora y su resultado en Sentinel.

**Preparación.** Abrí PowerShell en tu PC. Usá una suscripción de laboratorio con acceso al workspace `law-sc200-hunting`, en `rg-sc200-hunting`. Conservá la misma consola para los pasos siguientes.

~~~powershell
$PSVersionTable.PSVersion
# Si no hay una sesion iniciada: az login
az account show --query '{Suscripcion:name,Id:id}' -o table
$subId = az account show --query id -o tsv
$rgDemo = 'rg-sc200-hunting'
$workspace = az monitor log-analytics workspace list `
  --subscription $subId `
  --query "[?name=='law-sc200-hunting'] | [0]" -o json |
  ConvertFrom-Json
if (-not $workspace.id -or -not $workspace.customerId) {
    throw 'No se encontro law-sc200-hunting en la suscripcion activa.'
}
$workspace | Select-Object name, resourceGroup, id, customerId
~~~

Confirmá que el grupo y el workspace sean los del lab. `id` es el identificador ARM que se usa al configurar el destino. `customerId` identifica el workspace al consultarlo por CLI.

~~~powershell
az monitor diagnostic-settings subscription list `
  --subscription $subId -o json
~~~

**Comprobación.** Buscá un ajuste con `Administrative` habilitado y el destino del laboratorio. Si existe, pasá al paso 3.


## 2 Configurá la exportación si falta

Este bloque aplica al reconstruir el lab cuando todavía no hay un ajuste que envíe `Administrative` a ese workspace. Si el nombre elegido ya existe y apunta a otro destino, inspeccionalo antes de decidir si corresponde actualizarlo.

~~~powershell
$logsFile = New-TemporaryFile
try {
    '[{"category":"Administrative","enabled":true}]' |
      Set-Content -LiteralPath $logsFile.FullName -Encoding Ascii

    az monitor diagnostic-settings subscription create `
      --subscription $subId `
      --name 'sc200-activity-to-sentinel' `
      --workspace $workspace.id `
      --logs "@$($logsFile.FullName)" -o json
    if ($LASTEXITCODE -ne 0) {
        throw 'Azure CLI no pudo crear la configuracion.'
    }
}
finally {
    Remove-Item -LiteralPath $logsFile.FullName
}

az monitor diagnostic-settings subscription list `
  --subscription $subId -o json
~~~

Verificá `workspaceId`, `category: Administrative` y `enabled: true`. Desde el portal, la comprobación equivalente es **Suscripciones → suscripción del lab → Registro de actividad → Exportar registros de actividad**. Abrí el ajuste y comprobá el destino de Log Analytics.

**Si PowerShell rechaza `utf8NoBOM`.** Usá `Ascii` para este JSON, como en el bloque anterior.

**Si Azure devuelve `Conflict`.** Consultá los ajustes. Si la misma categoría ya se exporta al mismo destino, usá el ajuste existente.


## 3 Provocá un cambio e identificalo en Azure

Usá el grupo de recursos del lab. El valor con marca UTC hace que la etiqueta cambie cada vez. `Merge` conserva las demás etiquetas.

~~~powershell
$rgId = az group show --subscription $subId `
  --name $rgDemo --query id -o tsv
if (-not $rgId) { throw 'No se encontro el grupo de recursos.' }

$marcaDemo = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
az tag update --resource-id $rgId --operation Merge `
  --tags "SC200Demo=$marcaDemo" -o table
~~~

~~~powershell
az monitor activity-log list --subscription $subId `
  --resource-group $rgDemo --offset 1h `
  --query '[].{Hora:eventTimestamp,Operacion:operationName.value,Estado:status.value,CorrelationId:correlationId}' -o table
~~~

Buscá `Microsoft.Resources/tags/write` con estado `Succeeded`. Confirmá que la hora corresponde a tu prueba. Para obtener la última escritura exitosa de las últimas 24 horas, usá:

~~~powershell
$filtro = "[?operationName.value=='Microsoft.Resources/tags/write'"
$filtro += " && status.value=='Succeeded']"
$filtro = "sort_by($filtro, &eventTimestamp) | [-1]"

$evento = az monitor activity-log list --subscription $subId `
  --resource-group $rgDemo --offset 1d --query $filtro -o json |
  ConvertFrom-Json

if (-not $evento.correlationId) {
    throw 'No se encontro una escritura exitosa en ese intervalo.'
}
$evento | Select-Object eventTimestamp, correlationId
~~~

**Comprobación.** Anotá el `CorrelationId` y la hora de la escritura exitosa que corresponda a tu prueba.


## 4 Mostrá la evidencia en Defender

1. Abrí [Microsoft Defender](https://security.microsoft.com/) → **Búsqueda avanzada**.
2. Seleccioná **law-sc200-hunting** arriba a la derecha.
3. Pegá la consulta completa y presioná **Ejecutar consulta**. Ajustá el rango de la interfaz si corresponde.

~~~kusto
AzureActivity
| where TimeGenerated > ago(24h)
| top 20 by TimeGenerated desc
| project TimeGenerated, OperationNameValue, ActivityStatusValue,
          ResourceGroup, _ResourceId, CorrelationId
~~~

**Comprobación.** Identificá una operación administrativa y su estado. Si aparecen filas `Start` y `Failure`, compará sus `CorrelationId` para determinar si pertenecen al mismo intento. En operaciones a nivel de suscripción, `ResourceGroup` puede estar vacío.

## 5 Contrastá la prueba de etiqueta y cerrá el demo

En **Búsqueda avanzada**, reemplazá `<ID-DEL-EVENTO>` por el ID obtenido en el paso 3 y elegí un rango que incluya la hora de la prueba.

~~~kusto
AzureActivity
| where CorrelationId =~ "<ID-DEL-EVENTO>"
| project TimeGenerated, OperationNameValue, ActivityStatusValue,
          Caller, _ResourceId, CorrelationId
| order by TimeGenerated desc
~~~

**Comprobación por CLI.** Si Azure CLI pide instalar la extensión `log-analytics`, aceptá la instalación para ejecutar la consulta. Pasá el KQL como una sola cadena.

~~~powershell
$cid = $evento.correlationId
$kql = "AzureActivity | where CorrelationId =~ '$cid'"
$kql += ' | project TimeGenerated, OperationNameValue,'
$kql += ' ActivityStatusValue, CorrelationId'
az monitor log-analytics query --workspace $workspace.customerId `
  --analytics-query $kql --timespan P1D -o table
~~~

Para separar un filtro demasiado estricto de un problema de ingesta, consultá `AzureActivity` sin filtros de grupo. Si aparecen otros eventos, probá solo el filtro por operación.

~~~kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where OperationNameValue =~ "Microsoft.Resources/tags/write"
| project TimeGenerated, ActivityStatusValue, _ResourceId, CorrelationId
| order by TimeGenerated desc
~~~

Si la consulta general está vacía en Defender, corré esa misma consulta en **Azure Portal → law-sc200-hunting → Registros** y compará el resultado con el mismo intervalo.

**Entrega.** Mostrá la operación y su estado en Azure y en Sentinel con el mismo `CorrelationId`. Si la etiqueta todavía no aparece, indicá que su correlación está pendiente y adjuntá una fila de otra operación administrativa como evidencia de ingesta.

[Configuración de diagnóstico por suscripción](https://learn.microsoft.com/cli/azure/monitor/diagnostic-settings/subscription) · [Registro de actividad de Azure](https://learn.microsoft.com/azure/azure-monitor/fundamentals/activity-log)
