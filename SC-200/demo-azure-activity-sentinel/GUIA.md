# SC-200 · Investigar cambios administrativos de Azure en Sentinel

**Estado:** probado para ingesta y búsqueda en Defender. **Duración sugerida:** 5–8 minutos.

**Secuencia:** después de preparar el workspace de Sentinel. Presentarlo como demo independiente del evento 4625 de WIN1. Azure Activity aporta el registro administrativo de la suscripción. El 4625 aporta evidencia de un inicio de sesión fallido en Windows.

## Problema → solución → demo

**Problema:** Un cambio de configuración de Azure falló. El SOC necesita averiguar qué operación se intentó, cuándo ocurrió y cuál fue el resultado.

**Solución:** Exportar la categoría Administrative del Registro de actividad de Azure al workspace y consultar la tabla AzureActivity con KQL.

**Analogía:** Es la bitácora de cambios de Azure. El identificador de correlación permite reunir el inicio y el resultado de un mismo intento.

## Preparación

- Suscripción del lab y workspace `law-sc200-hunting` en `rg-sc200-hunting`.
- Usar la configuración de diagnóstico existente `subscriptionToSc200Hunting`, con `Administrative` habilitada hacia ese workspace.
- Verificación desde PowerShell con Azure CLI y la suscripción del lab seleccionada:

```powershell
$subId = az account show --query id -o tsv
az monitor diagnostic-settings subscription list --subscription $subId -o json
```

## Demostración verificada

1. Abrir Microsoft Defender → Búsqueda avanzada. Seleccionar `law-sc200-hunting`.
2. Ejecutar la consulta siguiente. Ajustar el rango a la fecha de los registros del lab.
3. Expandir la fila `Failure` y comparar su `CorrelationId` con el de la fila `Start`. Mostrar operación, hora y resultado.

```kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where OperationNameValue =~ "Microsoft.Insights/diagnosticSettings/write"
| top 20 by TimeGenerated desc
| project TimeGenerated, OperationNameValue, ActivityStatusValue,
          ActivitySubstatusValue, _ResourceId, CorrelationId
```

**Resultado esperado:** aparecen eventos administrativos consultables con KQL. Compará el inicio y el resultado por `CorrelationId`.

**Si aparecen cero filas:** comprobar el workspace y el rango. Quitar el filtro por operación para ver cualquier registro reciente. Si aún queda vacío, ejecutar la consulta en Registros de Log Analytics del mismo workspace. Para estas escrituras a nivel de suscripción, la evidencia observada tenía `ResourceGroup` vacío.

## Variante pendiente · Escritura de etiqueta

Para practicar la correlación de una escritura exitosa con la exportación activa:

```powershell
$rg = 'rg-sc200-hunting'
$rgId = az group show --subscription $subId --name $rg --query id -o tsv
if (-not $rgId) { throw 'No se encontró el grupo del lab.' }
$marca = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
az tag update --resource-id "$rgId" --operation Merge --tags "SC200Demo=$marca" -o table
az monitor activity-log list --subscription $subId --resource-group $rg --offset 1h --query "[?operationName.value=='Microsoft.Resources/tags/write'].{Hora:eventTimestamp,Estado:status.value,CorrelationId:correlationId}" -o table
```

En Defender, buscar `AzureActivity | where CorrelationId =~ "<ID del evento exitoso>"`. La variante queda probada cuando la escritura exitosa aparece con el mismo identificador en ambos lados.

**Cierre para clase:** “Azure registró el intento. En Sentinel podemos recuperar ese registro con KQL y relacionar el inicio con el resultado para entender qué pasó”.
