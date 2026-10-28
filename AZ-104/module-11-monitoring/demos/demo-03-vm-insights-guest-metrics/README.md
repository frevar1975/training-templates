# Demo · VM Insights clásico: métricas de Linux con KQL

**Curso:** AZ-104 · **Plantilla reutilizable** · **Módulo:** 11 · **Duración sugerida:** 35–40 minutos

## Objetivo

Crear desde cero un entorno aislado de supervisión para Linux y seguir las métricas del sistema operativo hasta Log Analytics: VM, workspace, Azure Monitor Agent (AMA), DCR clásica de VM Insights, asociación, carga de CPU y consultas KQL.

Esta guía usa la experiencia **clásica basada en registros**. La evidencia del demo se consulta en la tabla `InsightsMetrics` del workspace de Log Analytics.

## Guion de 35–40 minutos

| Minutos | Actividad |
|---|---|
| 0–4 | Presentar el escenario, elegir suscripción y explicar costos |
| 4–11 | Crear grupo, VM y workspace independientes |
| 11–17 | Asignar identidad e instalar AMA |
| 17–25 | Crear la DCR clásica y asociarla a la VM |
| 25–31 | Confirmar Heartbeat y métricas con KQL |
| 31–36 | Provocar carga controlada y graficar CPU |
| 36–40 | Interpretar el resultado y eliminar recursos |

## Historia para abrir

“Tenemos una VM Linux y queremos saber qué ocurre dentro del sistema operativo, no solo en el host de Azure. Configuraremos el agente y una regla de recopilación; luego generaremos carga y buscaremos CPU, memoria y disco en Log Analytics.”

## Requisitos y costos

- Suscripción con permisos para crear VM, identidad administrada, workspace, extensión y DCR.
- Azure CLI autenticado con `az login` en Windows PowerShell.
- Acceso a Azure Portal o al workspace para ejecutar KQL.
- Capacidad para una VM Linux pequeña, por ejemplo `Standard_B1s`, en `eastus`.
- La VM, disco, IP pública, workspace e ingestión de datos pueden generar cargos. Revisa cuotas y precios de tu suscripción.
- Usa un grupo nuevo dedicado a este demo; no lo mezcles con producción ni con otros laboratorios.
- No guardes IDs de suscripción, correos, direcciones IP ni credenciales en la plantilla.

## Paso 1 — Seleccionar suscripción y definir parámetros

En **Windows PowerShell** (no Bash), inicia sesión y comprueba la suscripción activa:

```powershell
az login
az account show --query "{Nombre:name, Id:id}" --output table
```

Selecciona el ID completo de la suscripción. No uses puntos suspensivos ni el nombre abreviado:

```powershell
az account set --subscription "TU-ID-COMPLETO-DE-SUSCRIPCION"
az account show --query "{Nombre:name, Id:id}" --output table
```

Define nombres nuevos para este laboratorio:

```powershell
$RG = "rg-demo-vminsights"
$LOCATION = "eastus"
$VM = "vm-demo-vminsights"
$WORKSPACE = "law-demo-vminsights"
$DCR = "dcr-demo-vminsights"
```

**Nota:** la sintaxis de PowerShell usa variables con `$`, por ejemplo `$RG = "rg-demo-vminsights"`. La sintaxis Bash `RG="rg-demo-vminsights"` no funciona en PowerShell.

## Paso 2 — Crear el grupo, VM y workspace

Crea el grupo dedicado:

```powershell
az group create --name $RG --location $LOCATION --output table
```

Crea una VM Ubuntu pequeña. No se abre SSH; el demo usa Azure Run Command:

```powershell
az vm create `
  --resource-group $RG `
  --name $VM `
  --image Ubuntu2204 `
  --size Standard_B1s `
  --admin-username azureuser `
  --generate-ssh-keys `
  --public-ip-sku Standard `
  --output table
```

Comprueba el estado:

```powershell
az vm get-instance-view `
  --resource-group $RG `
  --name $VM `
  --query "instanceView.statuses[].displayStatus" `
  --output table
```

Crea el workspace de Log Analytics en la misma región:

```powershell
az monitor log-analytics workspace create `
  --resource-group $RG `
  --workspace-name $WORKSPACE `
  --location $LOCATION `
  --output table
```

Confirma el nombre y la ubicación:

```powershell
az monitor log-analytics workspace show `
  --resource-group $RG `
  --workspace-name $WORKSPACE `
  --query "{Workspace:name, Ubicacion:location}" `
  --output table
```

## Paso 3 — Preparar AMA en la VM

Asigna identidad administrada del sistema y, después, instala la extensión AMA:

```powershell
az vm identity assign --resource-group $RG --name $VM --output table

az vm extension set `
  --name AzureMonitorLinuxAgent `
  --publisher Microsoft.Azure.Monitor `
  --vm-name $VM `
  --resource-group $RG `
  --enable-auto-upgrade true `
  --output table
```

Verifica que la extensión esté lista:

```powershell
az vm extension list `
  --resource-group $RG `
  --vm-name $VM `
  --query "[].{Nombre:name, Estado:provisioningState, Version:typeHandlerVersion}" `
  --output table
```

El estado esperado de la extensión es `Succeeded`. Espera a que termine antes de continuar.

## Paso 4 — Crear la DCR clásica de VM Insights

Obtén el ID del workspace y construye el JSON en PowerShell. **En `counterSpecifiers` escribe dos barras invertidas por cada separador: `\\VmInsights\\DetailedMetrics`. No escribas cuatro.** En JSON esas dos barras codifican una barra invertida real.

```powershell
$WORKSPACE_ID = az monitor log-analytics workspace show `
  --resource-group $RG `
  --workspace-name $WORKSPACE `
  --query id `
  --output tsv

$DCR_JSON = @"
{
  "location": "$LOCATION",
  "kind": "Linux",
  "properties": {
    "description": "DCR clásica de VM Insights para AZ-104",
    "dataSources": {
      "performanceCounters": [
        {
          "name": "VMInsightsPerfCounters",
          "streams": ["Microsoft-InsightsMetrics"],
          "scheduledTransferPeriod": "PT1M",
          "samplingFrequencyInSeconds": 60,
          "counterSpecifiers": ["\\VmInsights\\DetailedMetrics"]
        }
      ]
    },
    "destinations": {
      "logAnalytics": [
        {
          "workspaceResourceId": "$WORKSPACE_ID",
          "name": "VMInsightsPerf-Logs-Dest"
        }
      ]
    },
    "dataFlows": [
      {
        "streams": ["Microsoft-InsightsMetrics"],
        "destinations": ["VMInsightsPerf-Logs-Dest"]
      }
    ]
  }
}
"@

$DCR_FILE = "$env:TEMP\dcr-demo-vminsights.json"
$DCR_JSON | Set-Content -Path $DCR_FILE -Encoding ascii
```

Crea la DCR con `--kind Linux` **desde la primera ejecución**:

```powershell
az monitor data-collection rule create `
  --resource-group $RG `
  --location $LOCATION `
  --name $DCR `
  --kind Linux `
  --rule-file $DCR_FILE `
  --output table
```

El estado esperado es `Succeeded` y el tipo debe ser `Linux`. `kind` es inmutable: si intentas actualizar una DCR Linux omitiendo `--kind Linux`, la CLI puede enviar un valor vacío y Azure rechazará el cambio.

Confirma el contador guardado:

```powershell
az monitor data-collection rule show `
  --resource-group $RG `
  --name $DCR `
  --query "dataSources.performanceCounters[0].counterSpecifiers" `
  --output json
```

La salida JSON esperada es:

```json
[
  "\\VmInsights\\DetailedMetrics"
]
```

En la salida JSON, dos barras visibles representan una barra invertida real en el valor. Si aparecen cuatro barras visibles por separador, revisa el JSON antes de asociar la regla.

## Paso 5 — Asociar la DCR a la VM

Obtén los identificadores y crea la asociación:

```powershell
$VM_ID = az vm show --resource-group $RG --name $VM --query id --output tsv
$DCR_ID = az monitor data-collection rule show --resource-group $RG --name $DCR --query id --output tsv

az monitor data-collection rule association create `
  --name "assoc-vminsights-demo" `
  --rule-id $DCR_ID `
  --resource $VM_ID `
  --output table
```

Verifica que la regla esté asociada:

```powershell
az monitor data-collection rule association list-by-resource `
  --resource $VM_ID `
  --output table
```

## Paso 6 — Validar Heartbeat y métricas con KQL

Abre el workspace `law-demo-vminsights` en Azure Portal y selecciona **Logs**. Espera varios minutos después de crear la asociación antes de evaluar la llegada de datos.

Primero comprueba Heartbeat:

```kusto
Heartbeat
| where TimeGenerated > ago(2h)
| where Computer has "vm-demo-vminsights"
| summarize Ultimo=max(TimeGenerated), Muestras=count() by Computer, Category
```

Debe aparecer la VM con categoría `Azure Monitor Agent`. Heartbeat confirma que el agente se comunica con el workspace; todavía hay que comprobar la telemetría de VM Insights.

Consulta las métricas clásicas:

```kusto
InsightsMetrics
| where TimeGenerated > ago(1h)
| where Computer =~ "vm-demo-vminsights"
| where Origin == "vm.azm.ms"
| summarize Muestras=count(), Ultimo=max(TimeGenerated) by Namespace, Name, Origin
| order by Namespace asc, Name asc
```

En el ensayo se observaron filas de `Processor / UtilizationPercentage`, `Memory / AvailableMB`, métricas de `LogicalDisk` y `Computer / Heartbeat`, con origen `vm.azm.ms`.

## Paso 7 — Provocar carga y mostrar el gráfico de CPU

Desde PowerShell, ejecuta una carga breve (una CPU, dos minutos) mediante Run Command:

```powershell
az vm run-command invoke `
  --resource-group $RG `
  --name $VM `
  --command-id RunShellScript `
  --scripts "timeout 120s bash -c 'yes > /dev/null & wait'"
```

El comando puede tardar hasta dos minutos en devolver el resultado. No lo ejecutes varias veces en paralelo. Espera un par de minutos para que las muestras se ingieran y consulta el gráfico:

```kusto
InsightsMetrics
| where TimeGenerated > ago(30m)
| where Computer =~ "vm-demo-vminsights"
| where Origin == "vm.azm.ms"
| where Namespace == "Processor" and Name == "UtilizationPercentage"
| summarize CPU=avg(Val) by bin(TimeGenerated, 1m)
| render timechart
```

Si solo hay una muestra, espera a que lleguen más antes de presentar una tendencia. Para demostrar variación, compara la línea base con la carga y vuelve a ejecutar la consulta.

## Qué explicar durante el resultado

- AMA recopila datos del sistema operativo invitado.
- La DCR selecciona el origen, el flujo de datos, el destino y el recurso asociado.
- `InsightsMetrics` guarda las métricas clásicas consultadas por KQL.
- Una métrica de host, como CPU del host de Azure, no es lo mismo que una métrica del sistema operativo invitado.
- Heartbeat confirma actividad del agente; las filas de Processor, Memory y LogicalDisk demuestran que llegaron métricas de VM Insights.

## Solución de problemas aprendida durante el ensayo

- **El grupo aparece como no encontrado:** confirma la suscripción activa en la misma consola donde ejecutas el comando. PowerShell, Cloud Shell y otras ventanas pueden tener contextos distintos. Usa `az account show`, selecciona el ID completo con `az account set` y comprueba `az group list`.
- **La VM funciona, pero no aparece Heartbeat:** valida extensión AMA, identidad administrada, asociación, workspace y región; espera unos minutos.
- **Hay Heartbeat, pero `InsightsMetrics` está vacío:** revisa la DCR y la asociación; confirma que el flujo sea `Microsoft-InsightsMetrics`, que el destino sea el workspace correcto y que el contador esté escrito como `\\VmInsights\\DetailedMetrics` en el JSON.
- **La DCR falla con un error de tipo vacío frente a `Linux`:** vuelve a crearla pasando `--kind Linux`. El tipo no se puede cambiar después de crear la regla.
- **Se actualizó la DCR, pero el agente sigue usando la regla anterior:** permite varios minutos para la resincronización. En el ensayo, reiniciar AMA no fue suficiente; al recrear únicamente la asociación de la DCR, la configuración se volvió a propagar y después llegaron las filas. Para recrear una asociación, elimina solo la asociación de esta DCR y vuelve a crearla; luego espera y consulta KQL otra vez.
- **La vista nueva de Monitor está vacía, pero KQL tiene filas:** este demo valida la experiencia clásica. Las métricas OpenTelemetry se envían a un Azure Monitor workspace distinto y se consultan con PromQL. No uses una vista OpenTelemetry vacía para concluir que `InsightsMetrics` no está funcionando, ni mezcles ambos destinos en esta práctica.
- **PowerShell muestra `>>` mientras pegas un bloque:** pega únicamente el código, sin copiar el prompt `PS C:\>` ni los prefijos `>>`.

## Limpiar el laboratorio

Verifica el grupo antes de borrarlo. La eliminación borra la VM, discos, redes, workspace, DCR y asociaciones alojadas dentro del grupo:

```powershell
az group show --name $RG --output table
az group delete --name $RG --yes --no-wait
az group exists --name $RG
```

`az group exists` devuelve `false` cuando la eliminación termina. No ejecutes la limpieza sobre un grupo que contenga recursos que quieras conservar.

## Resultado del ensayo

- AMA quedó activo y Heartbeat confirmó el envío al workspace.
- Se observó `InsightsMetrics` con métricas de CPU, memoria y disco para la VM Linux.
- La DCR clásica se creó con `kind Linux` y la ruta correcta `\\VmInsights\\DetailedMetrics`.
- Al corregir una DCR ya creada, fue necesario volver a crear su asociación y esperar la propagación antes de ver las filas en KQL.
