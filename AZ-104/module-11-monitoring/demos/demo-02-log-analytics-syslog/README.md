# Demo · Azure Monitor: Syslog y consultas KQL en Log Analytics

**Curso:** AZ-104 · **Plantilla reutilizable** · **Módulo:** 11 · **Duración sugerida:** 30–35 minutos

## Objetivo

Seguir un evento del sistema Linux desde su origen hasta una consulta en Azure Monitor Logs: desplegar una VM independiente, crear un workspace de Log Analytics, asociar una regla de recopilación de datos (DCR) con Azure Monitor Agent (AMA), generar un mensaje Syslog de prueba y encontrarlo con KQL.

La VM y el workspace de esta demo son independientes de la práctica de métricas y alertas. Se crean en un grupo de recursos nuevo.

## Historia para abrir la demo

“Una métrica nos dice cuánto recurso consume una máquina, pero no necesariamente qué pasó dentro del sistema operativo. Vamos a configurar la recopilación de registros, generar un evento identificable y buscarlo en Log Analytics.”

## Guion de 30–35 minutos

| Minutos | Actividad |
|---|---|
| 0–4 | Presentar el objetivo, elegir suscripción/región y explicar costos |
| 4–10 | Crear un grupo de recursos y una VM Linux independiente |
| 10–14 | Crear el workspace de Log Analytics |
| 14–22 | Crear una DCR desde el portal, agregar la VM, Syslog y destino |
| 22–27 | Confirmar Heartbeat y revisar Syslog en KQL |
| 27–32 | Generar un mensaje de prueba y consultarlo |
| 32–35 | Explicar el flujo y eliminar el grupo temporal |

## Requisitos y costos

- Suscripción Azure con permisos para crear grupos de recursos, VM, workspace, DCR y asociaciones de DCR.
- Azure CLI instalado y autenticado con `az login`.
- Acceso al portal de Azure.
- Disponibilidad de una VM pequeña Linux en la región seleccionada (en el ensayo: `Standard_B1s` en `eastus`).
- No se guarda en el repositorio el ID de suscripción, direcciones IP, correo ni credenciales.
- La VM, disco, IP pública, workspace y datos ingeridos pueden generar cargos. Revisa precios y cuotas de tu suscripción.
- Elimina únicamente el grupo desechable creado para esta práctica al terminar.

## Paso 1 — Seleccionar la suscripción y crear un grupo nuevo

En PowerShell, inicia sesión y revisa la suscripción:

```powershell
az login
az account show --query "{name:name, id:id}" --output table
```

Selecciona el ID completo de la suscripción que usarás. No copies literalmente el texto de ejemplo:

```powershell
az account set --subscription "TU-ID-COMPLETO-DE-SUSCRIPCION"
az account show --query "{name:name, id:id}" --output table
```

Crea un grupo exclusivo para este demo:

```powershell
$RG = "rg-demo-loganalytics"
$LOCATION = "eastus"
$VM = "vm-demo-logs"
$WORKSPACE = "law-demo-loganalytics"

az group create --name $RG --location $LOCATION --output table
```

**Explicación para la clase:** este laboratorio tiene su propio grupo, VM y workspace; no depende de recursos creados para el demo de alertas.

## Paso 2 — Crear la VM Linux

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

No abras SSH para este ejercicio: la generación del evento se hará mediante Azure Run Command.

## Paso 3 — Crear el workspace de Log Analytics

```powershell
az monitor log-analytics workspace create `
  --resource-group $RG `
  --workspace-name $WORKSPACE `
  --location $LOCATION `
  --output table
```

La DCR y el workspace de destino deben estar en la misma región física. En este ejemplo ambos se crean en East US.

## Paso 4 — Crear la DCR en Azure Portal

1. En el portal, abre **Monitor > Data Collection Rules > Create**.
2. En **Basics**, configura:
   - **Rule name:** `dcr-demo-syslog`
   - **Subscription:** la suscripción usada en los pasos anteriores
   - **Resource group:** `rg-demo-loganalytics`
   - **Region:** `East US`
   - **Platform type:** `Linux`
3. En **Resources**, pulsa **Add resources**. Expande el grupo nuevo, selecciona `vm-demo-logs` y pulsa **Apply**. Comprueba que la VM aparezca en la lista.
4. En **Collect and deliver**, pulsa **Add new data source** y elige **Linux Syslog**.
5. Elige al menos la combinación de facility y severidad que usarás para el evento de prueba. Para este ensayo: facility `user`, severidad `Warning`.
6. Agrega como destino **Azure Monitor Logs** y selecciona el workspace `law-demo-loganalytics`.
7. Revisa y crea la regla.

El portal instala Azure Monitor Agent si es necesario y crea la asociación de la DCR a la VM. En la regla, revisa **Resources** para confirmar que `vm-demo-logs` aparezca. Un estado como **Passed initial checks** confirma las verificaciones iniciales de asociación; luego valida la llegada real consultando datos.

## Paso 5 — Confirmar Heartbeat con KQL

Abre el workspace `law-demo-loganalytics` y selecciona **Logs**. Ejecuta:

```kusto
Heartbeat
| where Category == "Azure Monitor Agent"
| where TimeGenerated > ago(30m)
| summarize UltimoHeartbeat = max(TimeGenerated) by Computer
```

Debe aparecer `vm-demo-logs`. El agente suele enviar un heartbeat por minuto; tras crear la DCR, permite unos minutos para que empiecen a llegar datos.

**Explicación para la clase:** Heartbeat confirma que el agente está comunicándose con Azure Monitor. Por sí solo no demuestra todavía que la regla esté enviando el tipo de log que queremos.

## Paso 6 — Revisar Syslog recibido

Ejecuta:

```kusto
Syslog
| where TimeGenerated > ago(30m)
| project TimeGenerated, Computer, Facility, SeverityLevel, SyslogMessage
| order by TimeGenerated desc
```

Al principio pueden aparecer eventos de inicio de `rsyslogd` y del sistema. La tabla `Syslog` contiene los eventos Linux que la DCR entrega al workspace.

## Paso 7 — Generar un evento identificable

Desde PowerShell, envía un comando Linux a la VM con Azure Run Command:

```powershell
az vm run-command invoke `
  --resource-group $RG `
  --name $VM `
  --command-id RunShellScript `
  --scripts "logger -p user.warning 'AZ104-DEMO: evento Syslog de prueba'"
```

El facility `user` y la severidad `warning` deben estar incluidos en la configuración de Syslog de la DCR. Si no coinciden, el agente filtrará el evento.

## Paso 8 — Buscar el evento con KQL

En **Logs** del workspace, ejecuta:

```kusto
Syslog
| where TimeGenerated > ago(30m)
| where SyslogMessage contains "AZ104-DEMO"
| project TimeGenerated, Computer, Facility, SeverityLevel, SyslogMessage
| order by TimeGenerated desc
```

Resultado esperado: una fila para `vm-demo-logs`, facility `user`, severidad `warning` y mensaje `AZ104-DEMO: evento Syslog de prueba`.

## Qué explicar durante el resultado

- **VM:** produce el evento del sistema.
- **Azure Monitor Agent:** recoge y reenvía eventos que coinciden con la regla.
- **DCR:** define el origen, los filtros (facility/severidad), el destino y los recursos asociados.
- **Log Analytics workspace:** almacena los registros.
- **KQL:** filtra, proyecta y ordena los resultados para investigar.

Una analogía: la VM es el lugar donde ocurre el evento; AMA es el mensajero; la DCR es la instrucción que indica qué recoger y a qué dirección llevarlo; el workspace es el archivo central y KQL es la forma de buscar dentro de ese archivo.

## Solución de problemas rápida

- **No hay Heartbeat:** confirma que estás consultando `law-demo-loganalytics`, que la VM está en **Resources** de la DCR y que el agente tenga tiempo para iniciar.
- **Hay Heartbeat, pero no aparece Syslog:** revisa que Linux Syslog esté agregado como origen y que el destino sea el workspace correcto.
- **No aparece el evento de prueba:** confirma que facility `user` y severidad `Warning` están incluidos en la DCR; genera el mensaje de nuevo y espera unos minutos.
- **La regla muestra la VM asociada, pero no hay registros:** la asociación no sustituye la validación de datos. Revisa el agente, la DCR y el workspace de destino.
- Consulta el período de tiempo de Logs; usa `ago(30m)` en las consultas de esta práctica.

## Limpiar los recursos del lab

La eliminación del grupo borra todos los recursos del laboratorio, incluidos VM, discos, red, IP, workspace y DCR que estén dentro del grupo. Antes de ejecutarlo, verifica el nombre del grupo:

```powershell
az group show --name rg-demo-loganalytics --output table
az group delete --name rg-demo-loganalytics --yes --no-wait
az group exists --name rg-demo-loganalytics
```

El comando final devuelve `false` cuando la eliminación concluye. No ejecutes la eliminación si el grupo contiene recursos que quieras conservar.

## Resultado del ensayo

- Se creó un grupo independiente `rg-demo-loganalytics`, una VM Ubuntu `vm-demo-logs` y un workspace `law-demo-loganalytics`.
- Se creó desde el portal la DCR `dcr-demo-syslog`, asociada a la VM y con destino al workspace.
- La consulta de Heartbeat mostró la VM.
- Se recibió y consultó el evento `AZ104-DEMO: evento Syslog de prueba` con facility `user` y severidad `warning`.
