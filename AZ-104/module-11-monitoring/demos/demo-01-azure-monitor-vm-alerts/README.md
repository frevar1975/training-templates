# Demo · Azure Monitor: métricas y alertas en una VM

**Curso:** AZ-104 · **Plantilla reutilizable** · **Módulo:** 11 · **Duración:** 40 minutos

## Objetivo

Seguir un incidente de principio a fin: crear una VM de laboratorio, observar la métrica de CPU, provocar carga controlada, crear una alerta de métricas y un grupo de acciones con Azure CLI, y configurar una segunda regla desde Azure Portal.

La demostración enseña la diferencia entre una métrica que muestra un cambio y una alerta que solo se dispara cuando se cumple su umbral y ventana de evaluación.

## Guion de 40 minutos

| Minutos | Actividad |
|---|---|
| 0–5 | Presentar el incidente y revisar suscripción, región y costos |
| 5–13 | Crear grupo de recursos y VM |
| 13–18 | Abrir el gráfico de CPU y observar la línea base |
| 18–25 | Crear grupo de acciones y alerta con Azure CLI |
| 25–31 | Generar carga de CPU y observar el pico |
| 31–37 | Crear una alerta de disco desde Azure Portal |
| 37–40 | Revisar alertas y eliminar recursos |

## Historia para abrir la demo

“Los usuarios informan que una aplicación está lenta. Vamos a crear una VM de laboratorio, observar sus métricas, provocar carga y configurar Azure Monitor para detectar una condición y avisar al responsable.”

## Requisitos y costos

- Suscripción de Azure con permisos para crear máquinas virtuales, grupos de recursos, reglas de alertas y grupos de acciones.
- Azure CLI instalado y autenticado con `az login`.
- Acceso a Azure Portal y a Cloud Shell.
- Capacidad disponible para una VM `Standard_B1s` en `eastus`.
- Un correo de prueba que el instructor controla. La dirección se introduce en la terminal, no se guarda en este repositorio.
- La VM, disco, IP pública y demás recursos pueden generar cargos mientras existan. Revisa precios y cuotas de tu suscripción antes de desplegar.

Usa exclusivamente el grupo desechable `rg-demo-monitor` para la práctica. No reutilices un grupo con recursos de producción. El ejemplo no abre una regla entrante SSH; las pruebas se ejecutan mediante Azure Run Command.

## Preparar el entorno

Abre PowerShell:

```powershell
az login
az account show --query "{name:name, id:id}" --output table
```

Selecciona la suscripción correcta usando su ID completo y define los parámetros:

```powershell
az account set --subscription "TU-ID-COMPLETO-DE-SUSCRIPCION"

$RG = "rg-demo-monitor"
$LOCATION = "eastus"
$VM = "vm-demo-monitor"
```

Crea el grupo de recursos y la VM:

```powershell
az group create --name $RG --location $LOCATION --output table

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

Confirma que la VM esté ejecutándose:

```powershell
az vm get-instance-view `
  --resource-group $RG `
  --name $VM `
  --query "instanceView.statuses[].displayStatus" `
  --output table
```

Si Cloud Shell inicia una sesión distinta, vuelve a seleccionar la suscripción allí. No asumas que hereda el contexto de PowerShell:

```bash
az account set --subscription "TU-ID-COMPLETO-DE-SUSCRIPCION"
az account show --query "{name:name, id:id}" --output table
az group show --name rg-demo-monitor --query "{name:name, location:location}" --output table
```

Si el grupo no aparece, comprueba la suscripción activa antes de continuar.

## Observar la línea base en el portal

En Azure Portal:

1. Abre **Máquinas virtuales > vm-demo-monitor**.
2. Selecciona **Supervisión > Métricas**.
3. Usa el espacio de métricas **Virtual Machine Host**.
4. Selecciona **Percentage CPU** y agregación **Avg**.
5. Muestra los últimos 30 minutos o la última hora.

**Explicación:** “Este gráfico muestra la línea base de la máquina. Una métrica ofrece un valor a lo largo del tiempo; por sí sola no determina si debemos generar una notificación.”

## Crear grupo de acciones y alerta con Azure CLI

En PowerShell, recupera el ID de la VM y define el correo del instructor:

```powershell
$VM_ID = az vm show `
  --resource-group $RG `
  --name $VM `
  --query id `
  --output tsv

$EMAIL = "CORREO-DEL-INSTRUCTOR"
```

Crea un grupo de acciones. Azure puede enviar un mensaje de verificación al destinatario:

```powershell
az monitor action-group create `
  --name "ag-demo-monitor" `
  --resource-group $RG `
  --short-name "DemoMon" `
  --action email "AvisoCPU" $EMAIL `
  --output table
```

Obtén el ID del grupo y crea una alerta para CPU promedio superior a 80 % durante una ventana de cinco minutos:

```powershell
$AG_ID = az monitor action-group show `
  --name "ag-demo-monitor" `
  --resource-group $RG `
  --query id `
  --output tsv

az monitor metrics alert create `
  --name "alerta-cpu-demo" `
  --resource-group $RG `
  --scopes $VM_ID `
  --condition "avg Percentage CPU > 80" `
  --window-size 5m `
  --evaluation-frequency 1m `
  --description "Demo AZ-104: CPU promedio superior al 80% durante 5 minutos" `
  --severity 2 `
  --action $AG_ID `
  --output table
```

Verifica la regla:

```powershell
az monitor metrics alert show `
  --name "alerta-cpu-demo" `
  --resource-group $RG `
  --query "{Nombre:name, Habilitada:enabled, Severidad:severity, Condiciones:criteria.allOf}" `
  --output json
```

**Explicación:** la regla combina ámbito (la VM), señal (Percentage CPU), agregación, umbral y ventana de evaluación. El grupo de acciones decide cómo se notifica al equipo.

## Provocar carga y observar CPU

En Cloud Shell Bash, confirma que la suscripción correcta está activa y ejecuta carga controlada durante tres minutos:

```bash
az account set --subscription "TU-ID-COMPLETO-DE-SUSCRIPCION"

az vm run-command invoke \
  --resource-group rg-demo-monitor \
  --name vm-demo-monitor \
  --command-id RunShellScript \
  --scripts "timeout 180s bash -c 'yes > /dev/null & yes > /dev/null & wait'"
```

El comando puede permanecer en estado **Running** durante la prueba. No lo ejecutes varias veces en paralelo. Vuelve al gráfico de **Percentage CPU**, pulsa **Refresh** y compara la línea con la línea base. En el ensayo de clase se observó un pico cercano al 100 %.

La alerta anterior exige un promedio superior al 80 % durante cinco minutos. Un pico puede aparecer en el gráfico y aun así no cumplir esa ventana. Usa esto para explicar por qué una alerta no se dispara por cualquier variación.

## Crear otra regla visualmente desde Azure Portal

Para contrastar la creación por CLI con la experiencia gráfica:

1. Abre **Monitor > Alerts > Create > Alert rule**.
2. En **Scope**, selecciona la suscripción, el grupo `rg-demo-monitor` y la VM `vm-demo-monitor`.
3. En **Condition**, selecciona **OS Disk IOPS Consumed Percentage**. La VM de esta demo no tiene un disco de datos adicional, por lo que **Data Disk IOPS Consumed Percentage** puede aparecer sin datos.
4. Revisa la vista previa del gráfico antes de crear la regla. Si no hay puntos de datos para la señal, no la uses para demostrar una alerta disparada.
5. Mantén agregación **Average**, operador **Greater than** y el umbral bajo de laboratorio elegido por el instructor (por ejemplo, 5 %). Revisa **Check every** y **Lookback period**.
6. En **Actions**, selecciona el grupo `ag-demo-monitor`.
7. En **Details**, usa un nombre identificable, por ejemplo `alerta-disco-demo-portal`, revisa la gravedad y pulsa **Review + create > Create**.

Para generar actividad de escritura en el disco del sistema operativo desde Cloud Shell:

```bash
az vm run-command invoke \
  --resource-group rg-demo-monitor \
  --name vm-demo-monitor \
  --command-id RunShellScript \
  --scripts "timeout 180s bash -c 'while :; do dd if=/dev/zero of=/var/tmp/monitor-demo.bin bs=1M count=32 oflag=direct conv=fdatasync status=none; done'; rm -f /var/tmp/monitor-demo.bin"
```

El archivo temporal se borra al terminar. Vuelve a **Métricas**, selecciona **OS Disk IOPS Consumed Percentage** y pulsa **Refresh**. La disponibilidad y el comportamiento de esta métrica dependen del disco y del intervalo de muestreo. Si no sube o no hay datos, presenta la configuración de la regla como contraste visual y usa la prueba de CPU como evidencia del pico.

**Explicación:** “La regla creada por CLI y la creada por el portal usan los mismos conceptos. Cambia la forma de configurar, no el modelo de ámbito, señal, condición y acción.”

## Cierre con preguntas

- ¿Qué nos enseñó la gráfica de CPU que no nos dijo la regla?
- ¿Por qué el pico cercano al 100 % puede no activar la alerta de cinco minutos?
- ¿Qué diferencia hay entre crear una regla por CLI y desde el portal?
- ¿Qué función cumple el grupo de acciones?
- ¿Qué revisarías si una señal aparece sin datos?

## Limpiar todos los recursos de la demo

Al terminar, elimina únicamente el grupo de recursos dedicado a esta práctica. Esto elimina la VM, discos, red, alertas y grupo de acciones alojados en él. La operación no se puede deshacer:

```powershell
az group show --name rg-demo-monitor --output table
az group delete --name rg-demo-monitor --yes --no-wait
az group exists --name rg-demo-monitor
```

El último comando devolverá `false` cuando la eliminación se complete.

## Resultado del ensayo

- VM Ubuntu `Standard_B1s` creada en `eastus`.
- Métrica de CPU visible en Azure Portal y carga de prueba con un pico cercano al 100 %.
- Regla CLI validada: `Percentage CPU > 80`, promedio, ventana `PT5M`, evaluación `PT1M`.
- La regla de CPU no necesariamente se dispara porque los picos fueron más breves que la ventana de cinco minutos.
- En el ensayo, la métrica de disco de datos no tenía datos; se usó la señal del disco del sistema operativo para la regla creada desde el portal.
- Revisar costos, datos y cuotas en cada suscripción antes de repetir la demo.
