# AZ-104 · Módulo 11 · Supervisión

Este módulo complementa la presentación y el Laboratorio 11 con una demostración guiada de Azure Monitor. Se crea una VM de laboratorio, se observa su métrica de CPU, se provoca carga controlada y se configuran reglas de alerta con Azure CLI y Azure Portal.

## Demo

- [Métricas y alertas de Azure Monitor en una VM](demos/demo-01-azure-monitor-vm-alerts/README.md)  
  Desplegar una VM Ubuntu pequeña, revisar Percentage CPU, crear un grupo de acciones y una alerta por CLI, provocar carga y crear una segunda regla desde el portal.

## Relación con el módulo

La presentación cubre Azure Monitor, métricas, registros y alertas. El Laboratorio 11 practica la implementación de supervisión. La demo refuerza el flujo de operación: recurso que emite telemetría, métrica visual, regla con una condición, grupo de acciones y verificación de alertas.

## Requisitos comunes

- Suscripción de Azure con permisos para crear VMs, grupos de recursos, alertas y grupos de acciones.
- Azure CLI y acceso a Azure Portal/Cloud Shell.
- Revisar costos, cuotas y disponibilidad de tamaños antes de crear recursos.
- Usar datos de prueba; no incluir direcciones de correo, IDs de suscripción ni credenciales en el repositorio.
- Eliminar los recursos temporales al terminar.

La regla de CPU usa una ventana promedio de cinco minutos. Un pico breve puede aparecer en el gráfico sin disparar la alerta. La métrica de IOPS depende del disco y puede no tener datos; comprobar la vista previa antes de usarla para una demostración.
