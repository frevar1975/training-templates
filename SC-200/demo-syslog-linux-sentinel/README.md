# Demo de ingesta de Syslog de Linux en Microsoft Sentinel

Guía reutilizable para demostrar cómo Sentinel recibe eventos de un equipo Linux mediante Syslog, Azure Monitor Agent (AMA) y una regla de recopilación de datos (DCR).

**Duración sugerida:** 30–45 minutos, incluida la creación de una VM nueva.  
**Terminal:** Windows PowerShell 5.1 con Azure CLI.  
**Privacidad:** no publiques identificadores de suscripción, secretos, claves SSH ni datos personales.

## Objetivo y recorrido

Generar un evento controlado en Linux y demostrar que aparece en Microsoft Sentinel. El recorrido es: **Linux genera el evento → AMA lo recoge → la DCR selecciona qué recopilar y a qué equipo aplicar las instrucciones → el workspace lo guarda en `Syslog` → el analista lo consulta con KQL**.

El conector instala el contenido y habilita la configuración de recopilación. Para esta ruta también se requiere AMA en la VM y una DCR asociada a ella.

## Requisitos

- Workspace de Log Analytics con Microsoft Sentinel habilitado.
- Azure CLI instalada y sesión iniciada con `az login`; contexto seleccionado en la suscripción de laboratorio.
- Permisos para crear una VM, habilitar AMA y crear/asociar una DCR.
- Costos potenciales por VM, disco, IP pública, Log Analytics y retención. Revisar los recursos antes de eliminar el grupo.

## 1. Crear un grupo de recursos para la VM

En PowerShell:

```powershell
az group create --name "rg-sc200-alert-demo" --location "eastus"
```

## 2. Crear una VM Ubuntu 22.04

```powershell
az vm create --resource-group "rg-sc200-alert-demo" --name "vm-linux-syslog-demo" --location "eastus" --image "Ubuntu2204" --size "Standard_B2s" --admin-username "azureuser" --generate-ssh-keys --nsg-rule "NONE"
```

`--nsg-rule "NONE"` evita crear una regla de entrada de SSH. La salida de esta práctica mostró una IP pública, aunque no se habilitó el acceso entrante en el NSG. Protege las claves SSH y considera la IP pública y los recursos asociados al estimar costos.

## 3. Instalar la solución y abrir el conector

En Microsoft Defender/Sentinel:

1. Abre **Microsoft Sentinel → Content management → Content hub**.
2. Busca e instala la solución **Syslog** si todavía no está instalada.
3. Abre la solución y selecciona el conector **Syslog via AMA**.
4. Abre la página del conector.

Instalar la solución agrega contenido. Todavía hay que configurar la recopilación y asociarla a la VM.

## 4. Crear y asociar la DCR

En **Configuration** del conector, selecciona **+ Create data collection rule**. Asigna un nombre, por ejemplo `dcr-syslog-linux-demo`.

En los filtros de Syslog, configura la instalación para este ejercicio:

- Facility: `LOG_LOCAL4`
- Minimum log level: `LOG_WARNING`
- Para otros facilities: deja `none`, salvo que el ejercicio requiera otros eventos.

Si el asistente solicita recursos, selecciona `vm-linux-syslog-demo`. Revisa y crea la regla. Vuelve a Configuration y confirma que aparezca en la lista del conector.

La DCR es la instrucción de recopilación. Asociarla a la VM le indica a Azure que ese equipo debe aplicar la regla.

## 5. Comprobar AMA y la asociación

En PowerShell, comprueba la extensión AMA:

```powershell
az vm extension list --resource-group "rg-sc200-alert-demo" --vm-name "vm-linux-syslog-demo" --query "[].{Nombre:name,Tipo:type,Estado:provisioningState}" -o table
```

Se espera `AzureMonitorLinuxAgent` con estado `Succeeded`.

Comprueba que haya una asociación de DCR con la VM. El comando oculta los identificadores y muestra solo el nombre de asociación y el grupo de recursos:

```powershell
az monitor data-collection rule association list --resource "$(az vm show --resource-group "rg-sc200-alert-demo" --name "vm-linux-syslog-demo" --query id -o tsv)" --query "[].{Asociacion:name,Grupo:resourceGroup}" -o table
```

Se espera una fila para la asociación. Si no aparece, vuelve al asistente de la DCR y confirma que la VM fue incluida.

## 6. Generar el evento de prueba

Envía un evento `local4.warning` con una etiqueta fácil de buscar:

```powershell
az vm run-command invoke --resource-group "rg-sc200-alert-demo" --name "vm-linux-syslog-demo" --command-id RunShellScript --scripts "logger -p local4.warning -t SC200-LINUX-DEMO 'Prueba Syslog Linux para Sentinel'"
```

`logger` escribe en el registro Syslog local de Linux. El comando de Azure puede volver al prompt sin imprimir un mensaje útil; confirma el resultado consultando la tabla.

## 7. Confirmar que AMA llega al workspace

En Logs del workspace o en Advanced hunting de Sentinel, ejecuta:

```kusto
Heartbeat
| where TimeGenerated > ago(1h)
| where Computer =~ "vm-linux-syslog-demo"
| project TimeGenerated, Computer, OSType
| order by TimeGenerated desc
```

Una fila reciente confirma que el agente se comunica con Azure Monitor. `Heartbeat` no demuestra por sí solo la recepción de eventos Syslog.

## 8. Consultar los eventos Syslog

```kusto
Syslog
| where TimeGenerated > ago(1h)
| where Computer =~ "vm-linux-syslog-demo"
| project TimeGenerated, Computer, Facility, SeverityLevel, SyslogMessage
| order by TimeGenerated desc
```

Para encontrar el evento específico:

```kusto
Syslog
| where TimeGenerated > ago(1h)
| where Computer =~ "vm-linux-syslog-demo"
| where SyslogMessage contains "SC200-LINUX-DEMO"
| project TimeGenerated, Computer, Facility, SeverityLevel, SyslogMessage
| order by TimeGenerated desc
```

El resultado esperado contiene facility `local4`, severidad `warning` y el texto de la prueba. La ingesta puede tardar varios minutos; usa una ventana de tiempo suficiente.

## Cómo explicarlo en clase

“Primero generamos un evento en un sistema Linux. AMA lo recoge y la DCR define qué clase de evento se acepta y a qué máquina se aplican esas instrucciones. El workspace lo guarda en la tabla `Syslog`. Finalmente, Sentinel permite buscarlo y revisar el equipo, el nivel de severidad y el mensaje.”

## Diagnóstico rápido

- **No hay `Heartbeat`:** revisar estado de la extensión `AzureMonitorLinuxAgent` y conectividad del agente.
- **Hay `Heartbeat`, no hay `Syslog`:** revisar que la DCR esté asociada a la VM, que incluya `LOG_LOCAL4` con `LOG_WARNING`, que el evento se haya generado y que el workspace correcto esté seleccionado.
- **Hay filas Syslog, no coincide la etiqueta:** consultar primero todos los eventos recientes de la VM y abrir `SyslogMessage`.
- **CLI retorna al prompt sin salida:** no lo tomes como evidencia del evento; la consulta KQL es la verificación.

## Limpieza opcional

Solo cuando termines, confirma que el grupo contiene únicamente recursos de esta práctica y que ya no los necesitas. La eliminación es irreversible para los recursos del grupo y detiene el demo:

```powershell
az group delete --name "rg-sc200-alert-demo" --yes --no-wait
```

No elimines el workspace `law-sc200-repo-demo` si se usa en otras prácticas.

## Referencias oficiales

- [Recopilar eventos Syslog con Azure Monitor Agent](https://learn.microsoft.com/azure/azure-monitor/vm/data-collection-syslog)
- [Solucionar problemas de Syslog con AMA en Linux](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-troubleshoot-linux-vm-rsyslog)
- [Asociaciones de reglas de recopilación de datos](https://learn.microsoft.com/azure/azure-monitor/data-collection/data-collection-rule-associations)
