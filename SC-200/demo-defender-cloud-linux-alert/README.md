# Demo SC-200: alerta Linux con Defender for Cloud y Sentinel

Guía escalonada para comparar la ingesta de registros antes de activar Defender for Servers y una detección de endpoint después de activarlo.

## Objetivo y alcance

Primero se demuestra que AMA + una DCR pueden recopilar Syslog. Después se habilitan Defender for Servers y la integración con Defender for Endpoint para Linux, se valida el sensor y se genera una detección de prueba EICAR. Sentinel consulta la alerta si el conector está conectado al workspace correcto.

AMA/DCR recopilan registros; no sustituyen a Defender for Endpoint ni detectan por sí solos la prueba de malware.

## Costos y alcance

Defender for Servers es un plan facturable. Antes de activarlo, revisa en el portal el precio vigente, si hay una prueba disponible y cuántos servidores cubre la suscripción. La configuración a nivel de suscripción puede aplicar a varias máquinas. La VM, sus discos y red, y Log Analytics también pueden tener costos propios.

## Fase 0 — Demostrar ingesta sin habilitar Servers

Mantén **Servers** desactivado durante esta fase.

1. Comprueba que la VM Linux de laboratorio ya tenga Azure Monitor Linux Agent (AMA) y una DCR de Syslog asociada.
2. Desde una sesión autorizada en la VM, envía un mensaje de prueba:
   ```bash
   logger -p local4.warning -t SC200-LINUX-DEMO 'Syslog antes de habilitar Defender for Servers'
   ```
3. En Sentinel → **Logs**, ejecuta:
   ```kusto
   Syslog
   | where TimeGenerated > ago(1h)
   | where ProcessName == "SC200-LINUX-DEMO"
   | project TimeGenerated, Computer, Facility, SeverityLevel, SyslogMessage
   | order by TimeGenerated desc
   ```
4. Revisa las extensiones de la VM. En esta fase puede aparecer AMA, pero no se espera todavía el sensor `MDE.Linux`.
5. No ejecutes EICAR ni presentes la prueba de Syslog como una alerta de Defender. Esta fase solo valida la recopilación.

## Fase 1 — Habilitar protección de servidores

Haz esta fase solo cuando quieras ejecutar la prueba de detección.

1. Abre **Microsoft Defender for Cloud → Environment settings → suscripción → Defender plans**.
2. Revisa el precio, la prueba disponible y el número/ámbito de servidores cubiertos. Guarda evidencia.
3. Habilita **Servers** si aceptas el alcance y las condiciones de costo mostradas.
4. En **Settings and monitoring**, deja **Endpoint protection** en **On**. Pulsa **Continue** y luego **Save**.
5. Deja la VM encendida y espera la incorporación. La instalación puede tardar hasta una hora; en la primera integración Linux de la suscripción, puede tardar hasta 12 horas.

## Fase 2 — Confirmar el sensor

En PowerShell, reemplaza los marcadores por tu grupo de recursos y VM:

```powershell
az vm extension list --resource-group "<grupo>" --vm-name "<vm>" --query "[].{Nombre:name,Estado:provisioningState}" -o table
```

Continúa solo cuando aparezca `MDE.Linux` con estado `Succeeded`. Luego consulta la protección en tiempo real:

```powershell
az vm run-command invoke --resource-group "<grupo>" --name "<vm>" --command-id RunShellScript --scripts "sudo mdatp health --field real_time_protection_enabled" --query "value[0].message" -o tsv
```

El resultado debe indicar `true`. Si devuelve `mdatp: command not found`, todavía no está instalado: no ejecutes EICAR; espera y revisa el estado detallado de la extensión y los requisitos de la VM.

## Fase 3 — Generar y revisar la detección

Solo en una VM desechable de laboratorio:

```bash
curl -O https://secure.eicar.org/eicar.com.txt
```

EICAR es un archivo inocuo de prueba para validar detecciones antimalware. Defender puede bloquearlo o ponerlo en cuarentena.

1. En Defender for Cloud → **Security alerts**, busca la alerta reciente y confirma que el recurso afectado es la VM de prueba.
2. En Sentinel, usa el workspace conectado y consulta:
   ```kusto
   SecurityAlert
   | where TimeGenerated > ago(1d)
   | where ProductName == "Azure Security Center"
   | where CompromisedEntity contains "<nombre-de-tu-VM>"
       or tostring(Entities) contains "<nombre-de-tu-VM>"
   | project TimeGenerated, AlertName, AlertSeverity, ProductName, CompromisedEntity
   | order by TimeGenerated desc
   ```
3. Si aparece en Defender for Cloud pero no en Sentinel, revisa el estado del conector, el workspace y los permisos. Las alertas de ejemplo `Sample-VM` no prueban que la VM real esté protegida.

## Fase 4 — Cerrar y controlar costos

1. Conserva evidencia de la ingesta Syslog, sensor, alerta y consulta.
2. Si no necesitas la protección continua, deshabilita **Servers** y guarda.
3. Revisa la configuración a nivel de recurso y **Cost Management** para confirmar que no quede cobertura facturable.
4. Detén o elimina la VM solo cuando confirmes que no se usa en otros laboratorios.

## Referencias oficiales

- [Integración de Defender for Endpoint y tiempos de incorporación](https://learn.microsoft.com/azure/defender-for-cloud/enable-defender-for-endpoint)
- [Validación de alertas](https://learn.microsoft.com/azure/defender-for-cloud/alert-validation)
- [Deshabilitar planes y comprobar cargos](https://learn.microsoft.com/azure/defender-for-cloud/disable-plans)
