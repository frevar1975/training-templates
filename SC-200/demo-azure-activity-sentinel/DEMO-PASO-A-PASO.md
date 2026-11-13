# Demo de ingesta de Azure Activity en Microsoft Sentinel

Guía base para preparar y presentar la demostración con un workspace de laboratorio.

**Duración:** 10 minutos para la ingesta; 10–15 minutos con la extensión de alerta.  
**Entorno:** Windows PowerShell 5.1, Azure CLI y Microsoft Sentinel.  
**Privacidad:** no escribas identificadores de suscripción, tokens ni datos personales en el repositorio.

## Objetivo y alcance

El grupo observa el recorrido de una operación administrativa desde Azure Activity hasta la tabla AzureActivity del workspace y la consulta KQL en Sentinel. Esta práctica usa registros de administración de Azure. No genera telemetría del sistema operativo ni una alerta de seguridad de un servidor.

Flujo de la demostración: Activity Log de Azure → conector y Azure Policy → Log Analytics → Microsoft Sentinel y consulta KQL.

## Antes de comenzar

- Tener un workspace Log Analytics con Microsoft Sentinel habilitado. En este ambiente se usa law-sc200-repo-demo.

- Tener instalada desde Content hub la solución Azure Activity.

- Contar con permisos para asignar Azure Policy al alcance de la suscripción, crear la identidad administrada, remediar y escribir en el workspace.

- Tener Azure CLI instalado e iniciar sesión con az login si se generará el evento desde PowerShell.

- Usar una suscripción de laboratorio. La ingestión y retención en Log Analytics pueden generar cargos.

## Paso 1 Mostrar la solución Azure Activity

En Microsoft Sentinel abre Content management → Content hub. Busca Azure Activity y muestra que la solución está instalada. Explica que la solución aporta contenido de Sentinel y que todavía hay que configurar el envío de los registros.

## Paso 2 Configurar el conector

> **Nota:** Si la asignación ya existe, no crees otra. Revisa primero el workspace, las categorías y el estado de remediación.

En Microsoft Sentinel abre Configuration → Data connectors → Azure Activity → Open connector page → Launch Azure Policy Assignment wizard.

- Basics: elige la suscripción como alcance para recopilar el Activity Log de esa suscripción.

- Parameters: selecciona el workspace law-sc200-repo-demo. Habilita Administrative para recibir operaciones de escritura como RESOURCEGROUPS/WRITE; marca otras categorías solo si forman parte del objetivo de la clase.

- Remediation: selecciona Create a remediation task para aplicar la configuración a los recursos existentes cuando corresponda.

- Managed identity: usa la identidad administrada del sistema que crea el asistente y conserva los permisos que asigna la definición de la política.

- Review + create: valida y crea la asignación. En Policy → Remediation → Remediation tasks, confirma que la tarea termine en Complete.

En la ejecución de esta práctica la tarea terminó en Complete, con 1 de 1 recursos completados.

## Paso 3 Generar una operación de prueba

Después de completar la remediación, actualiza una etiqueta del grupo de recursos de laboratorio. Así generas un evento nuevo y evitas depender de una operación anterior a la configuración.

```powershell
az group update --name "rg-sc200-alert-demo" --set tags.demo="sentinel-test"
```

La operación de escritura puede representar una creación o una actualización. En esta prueba se actualiza una etiqueta, así que descríbela como modificación del grupo de recursos.

## Paso 4 Consultar el evento en Sentinel

En el portal de Defender abre Microsoft Sentinel → Search o Advanced hunting y confirma que el workspace seleccionado sea law-sc200-repo-demo. Ejecuta primero esta consulta para ver los eventos Start y Success:

```kusto
AzureActivity
| where TimeGenerated > ago(1h)
| where ResourceGroup =~ "RG-SC200-ALERT-DEMO"
| where OperationNameValue =~ "MICROSOFT.RESOURCES/SUBSCRIPTIONS/RESOURCEGROUPS/WRITE"
| project TimeGenerated, Caller, OperationNameValue, ActivityStatusValue, ResourceGroup
| order by TimeGenerated desc
```

Para quedarte solo con la operación confirmada, agrega esta línea antes de project:

```kusto
| where ActivityStatusValue =~ "Success"
```

## Paso 5 Interpretar el resultado

Pide al grupo que identifique quién realizó la operación, cuándo ocurrió, qué acción se registró, sobre qué grupo y cuál fue el resultado. En AzureActivity, el estado exitoso aparece como Success. El Activity Log del portal o Azure CLI puede mostrar Succeeded.

| Hora local observada | Operación | Estado | Recurso |
| --- | --- | --- | --- |
| 13 nov 2026, 10:34:19–10:34:20 | RESOURCEGROUPS/WRITE | Start y Success | RG-SC200-ALERT-DEMO |

> **Nota:** En esta ejecución el panel del conector mostró Disconnected y, a la vez, Last Log Received reciente. La consulta de AzureActivity devolvió los eventos. Si aparece esta discrepancia, actualiza el panel y usa la consulta y la hora del último registro como evidencia de ingesta. No presentes el estado como Connected si la interfaz no lo muestra.

## Guion breve para explicar la lámina

> “La solución instala el contenido del conector. Luego configuramos el alcance, el workspace y las categorías que queremos enviar. Generamos una operación controlada y consultamos el registro en Sentinel para verificar quién actuó, qué hizo y si la operación terminó correctamente.”

## Extensión opcional Crear una alerta

Para continuar desde la ingesta hacia la detección, crea una regla de consulta programada desde Microsoft Sentinel → Configuration → Analytics → Create → Scheduled query rule.

- Nombre: Actividad de escritura en grupo de recursos demo.

- Severidad: Informational. No asignes una táctica ATT&CK a una operación administrativa genérica.

- Frecuencia: cada 5 minutos. Búsqueda de datos: última 1 hora. Inicio: Automatically.

- En Incident settings, habilita la creación de incidentes a partir de las alertas de esta regla.

```kusto
AzureActivity
| where TimeGenerated > ago(1h)
| where ResourceGroup =~ "RG-SC200-ALERT-DEMO"
| where OperationNameValue =~ "MICROSOFT.RESOURCES/SUBSCRIPTIONS/RESOURCEGROUPS/WRITE"
| where ActivityStatusValue =~ "Success"
| project TimeGenerated, Caller, OperationNameValue, ActivityStatusValue, ResourceGroup
```

> **Nota:** Una ventana de una hora puede volver a incluir el mismo evento en ejecuciones posteriores. Cuando confirmes la alerta o el incidente, deshabilita la regla de laboratorio para evitar detecciones repetidas. Esta alerta representa actividad del plano de administración de Azure, no un incidente de malware en un servidor.

## Criterios de éxito y cierre

- La solución Azure Activity aparece instalada en Content hub.

- La asignación de Azure Policy apunta al workspace esperado y su remediación figura como Complete.

- AzureActivity muestra el evento RESOURCEGROUPS/WRITE y el estado Success.

- El analista puede explicar Caller, TimeGenerated, OperationNameValue, ResourceGroup y ActivityStatusValue.

Si ya no necesitas el grupo vacío de prueba, puedes eliminarlo. Esto genera otro evento administrativo; conserva el grupo si quieres repetir la demostración.

```powershell
az group delete --name "rg-sc200-alert-demo" --yes --no-wait
```

No elimines el workspace ni la asignación de Azure Policy como parte del cierre de esta práctica, salvo que esa limpieza forme parte del plan del laboratorio.

## Referencias oficiales

- Conectar fuentes a Microsoft Sentinel con conectores basados en configuración de diagnóstico: https://learn.microsoft.com/azure/sentinel/connect-services-diagnostic-setting-based

- Crear reglas de análisis programadas en Microsoft Sentinel: https://learn.microsoft.com/azure/sentinel/create-analytics-rules
