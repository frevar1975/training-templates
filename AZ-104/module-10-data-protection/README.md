# AZ-104 · Módulo 10 · Protección de datos

Este módulo complementa la presentación y el Laboratorio 10 de AZ-104 con dos demostraciones operativas. La primera recupera un archivo eliminado desde un punto de Azure Backup; la segunda prueba la continuidad de una VM con Azure Site Recovery sin afectar la VM de origen.

## Demos

1. [Recuperación de un archivo con Azure Backup](demos/demo-01-azure-backup-file-recovery/README.md)  
   Crear un archivo de prueba en una VM protegida, esperar un punto de recuperación, eliminarlo y recuperarlo con File Recovery.
2. [Test Failover con Azure Site Recovery](demos/demo-02-asr-test-failover/README.md)  
   Replicar una VM Windows de Central US a West US 2, iniciar una VM temporal en una red aislada, validar IIS y limpiar el simulacro.

## Relación con el laboratorio oficial

El laboratorio oficial configura un Recovery Services vault, habilita Azure Backup para una VM, supervisa las copias y habilita la replicación. Estos demos refuerzan la evidencia práctica: recuperar un archivo individual y validar una recuperación regional con Test Failover.

## Requisitos comunes

- Suscripción de Azure con permisos para crear recursos y registrar proveedores.
- Azure CLI, Windows PowerShell 5.1 o PowerShell 7, y acceso a Azure Portal.
- Confirmar cuota y disponibilidad de tamaños en las dos regiones antes de iniciar.
- Usar una contraseña segura introducida de forma interactiva; nunca guardarla en el repositorio.
- Revisar costos y limpiar los recursos temporales al terminar.

Los nombres y rangos IP de los ejemplos son de laboratorio. Comprueba que los nombres estén libres en tu suscripción y que las redes no se superpongan con redes existentes.
