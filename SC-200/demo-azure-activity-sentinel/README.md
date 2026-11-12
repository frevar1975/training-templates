# SC-200 | Azure Activity -> Log Analytics -> Microsoft Sentinel

**Objetivo:** demostrar, de principio a fin, la ingestión de eventos administrativos de la suscripción Azure, su consulta en Log Analytics y la investigación mediante KQL en Microsoft Sentinel.

**Duración sugerida:** 35–50 minutos. **Terminal:** Windows PowerShell 5.1 (NO Bash). **Costo:** Log Analytics puede cobrar ingestión y retención. Usar una suscripción de laboratorio.

## Alcance de la demo

Esta práctica demuestra **generación -> exportación -> almacenamiento -> búsqueda**, no creación de reglas programadas, alertas o incidentes. La página de detalles de conectores no es imprescindible: se usa una configuración de diagnóstico de **nivel suscripción**.

## Requisitos

- Azure CLI instalada y sesión iniciada con `az login`.
- Permisos para consultar la suscripción, crear recursos, configurar diagnósticos a nivel suscripción y consultar Log Analytics.
- Un workspace Log Analytics asociado a Sentinel (puede existir desde otra práctica).
- Reemplazar los nombres e identificadores de ejemplo por los propios.
- No incluir tokens, credenciales ni exportaciones con datos sensibles en Git.

## 0. Variables y comprobación inicial (PowerShell)

```powershell
# Adaptar antes de impartir
$subscriptionId = "<SUBSCRIPTION_ID>"
$resourceGroup = "<RG_WORKSPACE>"
$workspaceName = "<LOG_ANALYTICS_WORKSPACE>"
$testResourceGroup = "rg-sc200-test-activity"
$diagnosticName = "diag-azureactivity-sc200"
$location = "eastus"

az login
az account set --subscription $subscriptionId
az account show --query "{Nombre:name,Id:id,Estado:state}" -o json
az monitor log-analytics workspace show --resource-group $resourceGroup --workspace-name $workspaceName --query "{Nombre:name,Estado:provisioningState,Id:id}" -o json
```

Si se parte de una suscripción completamente vacía y se dispone de permisos, crear primero el grupo y el workspace:

```powershell
az group create --name $resourceGroup --location $location
az monitor log-analytics workspace create --resource-group $resourceGroup --workspace-name $workspaceName --location $location
```

**Importante:** crear un workspace no habilita por sí mismo Sentinel. Si aún no se ha incorporado el workspace a Microsoft Sentinel, completar su onboarding por el portal y verificarlo antes de las consultas en Defender.

## 1. Comprobar la exportación actual

```powershell
az monitor diagnostic-settings subscription list --subscription $subscriptionId -o json
```

- `{"value":[]}` = no hay configuraciones de diagnóstico de suscripción.
- Si ya existe una, revisar su `workspaceId` y las categorías **antes de crear otra**; evitar exportación duplicada.

## 2. Obtener el ID del workspace

```powershell
$workspaceId = az monitor log-analytics workspace show --resource-group $resourceGroup --workspace-name $workspaceName --query id -o tsv
Write-Host $workspaceId
if (-not $workspaceId) { throw "No se obtuvo el workspace ID" }
```

El identificador tiene la forma `/subscriptions/.../resourceGroups/.../providers/Microsoft.OperationalInsights/workspaces/...`, distinto del `customerId`.

## 3. Habilitar los registros de actividad de la suscripción

Solo si el paso 1 confirma que no hay un diagnóstico equivalente:

```powershell
$logs = @(
    @{ category = "Administrative"; enabled = $true }
    @{ category = "Security"; enabled = $true }
    @{ category = "ServiceHealth"; enabled = $true }
    @{ category = "Alert"; enabled = $true }
    @{ category = "Recommendation"; enabled = $true }
    @{ category = "Policy"; enabled = $true }
    @{ category = "Autoscale"; enabled = $true }
    @{ category = "ResourceHealth"; enabled = $true }
) | ConvertTo-Json -Depth 5 -Compress

$logFile = Join-Path $env:TEMP "sentinel-activity-logs.json"
$logs | Set-Content -Path $logFile -Encoding UTF8

az monitor diagnostic-settings subscription create --name $diagnosticName --location $location --workspace $workspaceId --logs "@$logFile" -o json
az monitor diagnostic-settings subscription show --name $diagnosticName -o json
```

La respuesta de diagnóstico puede mostrar `location: global` aunque se pase `eastus`. Comprobar las ocho categorías `enabled: true` y la ruta exacta de `workspaceId`.

## 4. Generar una operación administrativa inocua

```powershell
az group create --name $testResourceGroup --location $location
az group show --name $testResourceGroup --query "{Nombre:name,Estado:properties.provisioningState}" -o json
```

Si el grupo ya existe, `az group create` puede no generar el mismo evento nuevo esperado. Usar un nombre temporal nuevo para otra impartición.

## 5. Consultar el Activity Log original

```powershell
az monitor activity-log list --offset 2h --max-events 30 --query "[].{Fecha:eventTimestamp,Operacion:operationName.value,Estado:status.value,Grupo:resourceGroupName}" -o table
```

Buscar `Microsoft.Resources/subscriptions/resourcegroups/write` con estados `Started` y `Succeeded`. Un filtro `--resource-group` puede comportarse distinto según el ámbito del evento; para la demo usar la consulta general mostrada.

## 6. Confirmar ingestión en Log Analytics con Azure CLI

```powershell
$workspaceGuid = az monitor log-analytics workspace show --resource-group $resourceGroup --workspace-name $workspaceName --query customerId -o tsv
Write-Host $workspaceGuid
az monitor log-analytics query --workspace $workspaceGuid --analytics-query "AzureActivity | where TimeGenerated > ago(4h) | summarize TotalEventos=count(), UltimoEvento=max(TimeGenerated)" -o json
az monitor log-analytics query --workspace $workspaceGuid --analytics-query "AzureActivity | where TimeGenerated > ago(4h) | project TimeGenerated, OperationNameValue, ActivityStatusValue, ResourceGroup, Caller | order by TimeGenerated desc" -o table
```

La exportación no es instantánea. Si `TotalEventos=0`, revisar tiempo transcurrido, ámbito de suscripción, identificador de workspace, categorías y el selector temporal; no recrear recursos a ciegas.

## 7. Investigar con KQL en Microsoft Defender

Abrir `https://security.microsoft.com` -> **Búsqueda avanzada**, y seleccionar el workspace correcto. Pegar **solo KQL**, nunca `$query = @'` (eso pertenece a PowerShell):

```kusto
AzureActivity
| where TimeGenerated > ago(4h)
| where OperationNameValue in~ (
    "Microsoft.Resources/subscriptions/resourcegroups/write",
    "Microsoft.Resources/subscriptions/resourcegroups/delete"
)
| where ActivityStatusValue =~ "Success"
| project TimeGenerated, Caller, OperationNameValue, ResourceGroup, ActivityStatusValue
| order by TimeGenerated desc
```

**Atención:** Azure CLI para Activity Log puede devolver `Succeeded` y la tabla `AzureActivity` devuelve `Success`; filtrar con el valor real del campo. `write` puede significar creación **o modificación**, no necesariamente creación exclusiva. El portal puede mostrar la hora convertida a zona local y Azure CLI habitualmente en UTC.

## 8. Explicación docente y criterios de éxito

Preguntas: **¿qué ocurrió?, ¿quién?, ¿cuándo?, ¿sobre qué recurso?, ¿con qué resultado?** Confirmar una fila `RESOURCEGROUPS/WRITE`, estado `Success`, usuario y grupo de prueba. Explicar la diferencia entre **Activity Log** (fuente), **Diagnostic Settings** (exportación), **Log Analytics** (almacenamiento) y **Sentinel/Advanced Hunting** (investigación).

**No se demuestra** alerta, analítica programada ni incidente. Quedan para un laboratorio posterior.

## 9. Si falla la página Connector details

Si aparece `NormalizationProvider is required`, registrar el mensaje, sesión y versión del módulo; intentar sesión privada u otro navegador. Puede tratarse de un error de frontend, y **no prueba** fallo de ingestión. Continuar con Diagnostics + CLI + KQL. No borrar el workspace ni cambiar RBAC por ese stack trace solamente.

## 10. Limpieza opcional

```powershell
# Solo si el grupo temporal no contiene recursos de otros laboratorios
az group delete --name $testResourceGroup --yes --no-wait

# Solo si se desea dejar de exportar eventos; esto detiene la ingestión futura
# az monitor diagnostic-settings subscription delete --name $diagnosticName
```

## Evidencias sugeridas

1. Listado de diagnostic settings antes/después.
2. JSON de configuración con ocho categorías y workspaceId.
3. Activity Log con operación `resourcegroups/write`.
4. Consulta CLI `AzureActivity` con total mayor que cero.
5. Consulta KQL en Advanced Hunting con identidad, recurso, hora y resultado.

**Fuentes de referencia:** [Azure Activity Log](https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log), [Exportar Activity Log](https://learn.microsoft.com/azure/azure-monitor/essentials/activity-log#export-activity-log), [Reglas de análisis de Sentinel](https://learn.microsoft.com/azure/sentinel/detect-threats-built-in).
