# AZ-104 · Módulo 11 · Supervisión

Este módulo complementa la presentación y el Laboratorio 11 con demostraciones guiadas de Azure Monitor.

## Demos

- [Métricas y alertas de Azure Monitor en una VM](demos/demo-01-azure-monitor-vm-alerts/README.md)  
  Desplegar una VM Ubuntu pequeña, revisar Percentage CPU, crear un grupo de acciones y una alerta por CLI, provocar carga y crear una segunda regla desde el portal.
- [Log Analytics: recopilar Syslog y consultar con KQL](demos/demo-02-log-analytics-syslog/README.md)  
  Crear un laboratorio independiente con su propio grupo, VM y workspace; configurar AMA y una DCR desde el portal; generar un evento Syslog y localizarlo con KQL.
- [VM Insights clásico: métricas de Linux con KQL](demos/demo-03-vm-insights-guest-metrics/README.md)  
  Crear un entorno independiente desde PowerShell, instalar AMA, crear y asociar una DCR clásica con Azure CLI, generar carga breve y consultar CPU, memoria y disco en `InsightsMetrics`.

## Relación con el módulo

La presentación cubre Azure Monitor, métricas, registros y alertas. El Laboratorio 11 practica la implementación de supervisión. La primera demo refuerza el flujo de operación con métricas y alertas. La segunda muestra cómo recopilar telemetría Syslog del sistema operativo Linux. La tercera muestra cómo recolectar métricas del sistema operativo invitado y analizarlas con KQL.

La tercera demo usa la ruta clásica basada en registros, cuyo destino es Log Analytics y cuya consulta es KQL. OpenTelemetry usa un Azure Monitor workspace separado y PromQL; no se usa para validar `InsightsMetrics` en esta práctica.

## Requisitos comunes

- Suscripción de Azure con permisos para crear los recursos de cada demo.
- Azure CLI y acceso a Azure Portal/Cloud Shell.
- Revisar costos, cuotas y disponibilidad de tamaños antes de crear recursos.
- Usar datos de prueba; no incluir direcciones de correo, IDs de suscripción ni credenciales en el repositorio.
- Eliminar los recursos temporales al terminar.

La regla de CPU de la demo 1 usa una ventana promedio de cinco minutos. Un pico breve puede aparecer en el gráfico sin disparar la alerta. La métrica de IOPS depende del disco y puede no tener datos; comprobar la vista previa antes de usarla para una demostración. La demo 2 crea recursos independientes y valida el envío de registros Syslog mediante Heartbeat y un evento identificable consultado con KQL. La demo 3 valida Heartbeat y `InsightsMetrics`; después de modificar una DCR, puede ser necesario esperar la resincronización o recrear su asociación para que AMA reciba la configuración nueva.
