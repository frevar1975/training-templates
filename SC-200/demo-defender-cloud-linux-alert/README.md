# Demo: alerta de seguridad en una VM Linux con Defender for Cloud y Sentinel

Guía reutilizable para un laboratorio SC-200. La VM debe ser de prueba y estar protegida por Defender for Servers y Defender for Endpoint antes de generar una detección.

**Duración sugerida:** 35–50 minutos, más el aprovisionamiento del sensor.

## Objetivo

Validar el recorrido de una detección segura de prueba: Defender for Endpoint detecta EICAR en Linux, Defender for Cloud presenta la alerta asociada al servidor y Microsoft Sentinel puede recibirla en `SecurityAlert` si el conector está operativo.

Azure Monitor Agent (AMA) y una regla de recopilación de datos (DCR) recopilan registros como Syslog. No sustituyen al sensor de Defender for Endpoint ni generan por sí solos una alerta de malware.

## Costos antes de empezar

Defender for Servers es un plan facturable. Antes de habilitarlo, revisa el precio vigente que muestra tu suscripción y cuántos servidores quedarán cubiertos. El ámbito de suscripción puede incluir más de una máquina. La VM, sus discos, red, Log Analytics y la ingesta o retención también pueden generar cargos.

## Requisitos

- Suscripción de Azure de laboratorio y permisos para configurar Defender for Cloud.
- VM Linux desechable, sin datos de producción.
- Workspace de Microsoft Sentinel, si se demostrará la consulta allí.
- Conectividad HTTPS de la VM con los servicios de Defender for Endpoint.
- Ubuntu 20.04 o posterior requiere Python 3 para el despliegue automático del sensor.

## Pasos

1. En **Microsoft Defender for Cloud → Environment settings → suscripción → Defender plans**, revisa el costo y el número de servidores. Habilita **Servers** solo si aceptas el cargo y el alcance mostrado.
2. En **Monitoring coverage → Settings**, revisa **Endpoint protections**. Si faltan componentes de Linux, selecciona **Fix → Missing components → Linux machines → Enable**. Guarda y continúa.
3. Espera la instalación del sensor. En la VM, confirma que la extensión `MDE.Linux` esté en estado `Succeeded`. Comprueba la protección en tiempo real:
   ```bash
   sudo mdatp health --field real_time_protection_enabled
   ```
   Debe devolver `true`. AMA no reemplaza este sensor.
4. Solo en la VM desechable de laboratorio, descarga el archivo EICAR de prueba:
   ```bash
   curl -O https://secure.eicar.org/eicar.com.txt
   ```
   EICAR es una cadena inocua de prueba reconocida por productos antimalware. Defender puede bloquear o poner el archivo en cuarentena.
5. En **Microsoft Defender for Cloud → Security alerts**, busca la alerta reciente y confirma que el recurso afectado corresponde a la VM del laboratorio.
6. En el workspace correcto de Sentinel, consulta la tabla:
   ```kusto
   SecurityAlert
   | where TimeGenerated > ago(1d)
   | where ProductName == "Azure Security Center"
   | where CompromisedEntity contains "<nombre-de-tu-VM>"
       or tostring(Entities) contains "<nombre-de-tu-VM>"
   | project TimeGenerated, AlertName, AlertSeverity, ProductName, CompromisedEntity
   | order by TimeGenerated desc
   ```
   Sustituye el marcador por el nombre de la VM. Si la alerta aparece en Defender for Cloud pero no en Sentinel, revisa el estado del conector, el workspace seleccionado y los permisos.
7. Al terminar, si no necesitas cobertura continua, desactiva **Servers** y comprueba si quedan servidores cubiertos. Detén o elimina la VM solo si sabes que no se usa en otros laboratorios.

La validación EICAR suele generar una alerta en unos minutos. Las alertas de ejemplo asociadas a recursos `Sample-VM` sirven para practicar consultas, pero no demuestran que una VM real esté protegida.

## Guion breve

“AMA y la DCR recogen registros; Defender for Endpoint analiza la VM y detecta la prueba EICAR; Defender for Cloud muestra la alerta asociada al servidor; Sentinel puede centralizarla si el conector está activo. Defender for Servers tiene un costo: revisamos el precio y el alcance de cobertura antes de habilitarlo.”

## Referencias oficiales

- [Validación de alertas](https://learn.microsoft.com/azure/defender-for-cloud/alert-validation)
- [Integración de Defender for Endpoint](https://learn.microsoft.com/azure/defender-for-cloud/enable-defender-for-endpoint)
- [Habilitar Defender for Servers](https://learn.microsoft.com/azure/defender-for-cloud/tutorial-enable-servers-plan)
