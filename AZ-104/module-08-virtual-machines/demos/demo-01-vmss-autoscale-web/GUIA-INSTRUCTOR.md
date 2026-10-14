> Plantilla común: elegir un entorno independiente por edición y sustituir el nombre de ejemplo en todos los comandos. El instructor confirmó el escalado real en Azure; los tiempos dependen de carga, cuota y región.

# Guía del instructor

Preparación del clon y despliegue abreviado: [README](README.md). Todos los comandos azd se ejecutan dentro de la carpeta que contiene azure.yaml. La guía utiliza el entorno az104-m08-vmss.

# Escalado provocado de una web con azd

Guía del instructor para el módulo 8 de AZ104

Desplegaremos con azd up una página participativa sobre un Virtual Machine Scale Set Ubuntu. Los siete alumnos enviarán solicitudes que consumen CPU y un script del instructor reforzará la carga. Azure Monitor agregará una segunda VM cuando la CPU promedio supere 60 en una ventana de cinco minutos; al finalizar la actividad, reducirá a una instancia si el promedio cae por debajo de 25 durante cinco minutos.

## Qué contiene esta versión

azure.yaml configura el proyecto azd. infra/main.bicep crea el grupo a nivel de suscripción; infra/web.bicep crea red, NSG, IP, balanceador, VMSS y autoscaling. infra/main.parameters.json conecta variables del entorno azd con los parámetros Bicep. cloud-init.yaml instala la aplicación automáticamente en cada nueva VM.

La aplicación se instala durante el aprovisionamiento de las VMs. Por eso azure.yaml no declara servicios separados y no hay una fase de publicación de código a App Service o Container Apps. azd up orquesta el aprovisionamiento que deja la web funcionando.

## Resultado visible

- La web muestra el nombre de la VM que responde y el tiempo de cálculo.

- Los alumnos pueden generar trabajo una vez o continuamente.

- El portal muestra CPU, ejecución de la regla y el paso de una a dos instancias.

- Al detener la carga se observa la reducción de dos a una instancia.

## Validación y preparación

El backend fue probado localmente y los archivos de configuración fueron revisados. La preparación original no dispuso de acceso a Azure; posteriormente el instructor validó el despliegue y el escalado. Debes ensayar antes de clase para confirmar permisos, cuota y tiempos reales. Este proyecto usa el entorno az104-m08-vmss y crea rg-az104-m08-vmss; no elimina ni reutiliza el grupo de las versiones anteriores.

## 2 Iniciar sesión y preparar el entorno azd

Inicia sesión en azd. Azure CLI usa su propia sesión: entra también en az para ejecutar comprobaciones posteriores. Usa la misma cuenta, tenant y suscripción.

```powershell
azd auth login
az login
az account list --output table
```

Copia el ID de la suscripción de laboratorio. Reemplaza el valor del siguiente bloque antes de ejecutarlo.

```powershell
$Suscripcion = "TU-ID-DE-SUSCRIPCION"
az account set --subscription $Suscripcion
az account show --output table
```

Crea un entorno nuevo y configura la región de todos los recursos. Si ya existe az104-m08-vmss en este proyecto, usa azd env select az104-m08-vmss en lugar de env new.

```powershell
azd env new az104-m08-vmss
azd env set AZURE_SUBSCRIPTION_ID $Suscripcion
azd env set AZURE_LOCATION eastus2
azd env set VM_SIZE Standard_D2s_v5
```

El siguiente script prepara una clave pública RSA requerida por la configuración Linux y la guarda en el entorno azd. No conserva una clave privada para conectarse por SSH: la red no expone SSH y la administración del demo es mediante Run Command. Si el entorno ya tiene clave, la reutiliza.

```powershell
.\scripts\Preparar-Clave.ps1
```

Comprueba las variables principales. SSH_PUBLIC_KEY contiene solo una clave pública.

```powershell
azd env get-value AZURE_ENV_NAME
azd env get-value AZURE_LOCATION
azd env get-value VM_SIZE
```

Registra proveedores si tu suscripción aún no los tiene registrados. Este paso puede tardar varios minutos.

```powershell
az provider register --namespace Microsoft.Compute --wait
az provider register --namespace Microsoft.Network --wait
az provider register --namespace Microsoft.Insights --wait
```

## 3 Desplegar con azd up

Ejecuta desde la raíz del proyecto. azd lee azure.yaml, sustituye las variables de main.parameters.json y despliega main.bicep a nivel de suscripción. Bicep crea el grupo y llama al módulo web.

```powershell
azd up
```

Si solicita suscripción o región, verifica que sean las elegidas. Mantén la terminal abierta. Se crean una VNet, subred, NSG, IP Standard, Load Balancer, una VMSS Uniform y autoscaling. El balanceador publica HTTP en 80 hacia el backend 8080; una sonda /health verifica cada instancia. La regla de salida permite conectividad explícita hacia fuera.

Puede aparecer que no hay servicios que desplegar: esta plantilla usa aprovisionamiento e instalación por cloud-init, sin un servicio separado de azd. Comprueba el éxito de la infraestructura y la web. Para repetir solo el aprovisionamiento puedes usar azd provision.

Cuando termine, consulta la URL y las salidas del entorno. El script Obtener-Url guarda una copia local para el instructor.

```powershell
.\scripts\Obtener-Url.ps1
$Url = (azd env get-value DEMO_URL).Trim()
$Rg = (azd env get-value AZURE_RESOURCE_GROUP).Trim()
$Vmss = (azd env get-value VMSS_NAME).Trim()
$VmssId = (azd env get-value VMSS_ID).Trim()
$Url
$Rg
```

Si no aparecen las salidas después de un despliegue exitoso, ejecuta azd env refresh y repite el bloque. Una VM aprovisionada aún puede estar terminando cloud-init. Espera a que la sonda y la página respondan antes de compartir la dirección.

## Si falla por cuota o tamaño

```powershell
az vm list-usage --location eastus2 --output table
az vm list-sizes --location eastus2 --output table
```

Selecciona un tamaño no burstable de dos vCPU con cuota disponible. Configúralo mediante azd env set VM_SIZE NUEVO-TAMANO y vuelve a ejecutar azd provision después de revisar el error. Evita cambiar de región sobre un grupo ya existente: conserva su región o usa un entorno nuevo para otra región.

## 4 Verificar la web y diagnosticar

```powershell
az vmss list-instances -g $Rg -n $Vmss --output table
curl.exe --connect-timeout 5 --max-time 10 "$Url/health"
curl.exe --connect-timeout 5 --max-time 30 "$Url/work"
Start-Process $Url
```

Resultado esperado: una instancia; /health devuelve ok; /work devuelve server y seconds; la portada presenta Generar trabajo, Participar continuamente y Detener mi participación. Escribe http:// explícitamente si el navegador intenta HTTPS.

Si la página aún no responde, espera uno o dos minutos y repite las pruebas. Si persiste, revisa servicio y cloud-init con Run Command.

```powershell
$Instancia = az vmss list-instances -g $Rg -n $Vmss --query "[0].instanceId" -o tsv
az vmss run-command invoke -g $Rg -n $Vmss `
  --instance-id $Instancia --command-id RunShellScript `
  --scripts "cloud-init status --long; systemctl status az104-web --no-pager; curl -s http://127.0.0.1:8080/health; journalctl -u az104-web -n 25 --no-pager"
```

Si la sonda local responde, revisa lb-demo → Backend pools y Health probes. La sonda consulta /health en 8080. La regla de balanceo conecta puerto público 80 con 8080 y el NSG permite web y las sondas. Esta herramienta temporal no solicita credenciales ni maneja datos personales.

## Reabrir el entorno otro día

```powershell
Set-Location C:\GithubOrden\training-templates\AZ-104\module-08-virtual-machines\demos\demo-01-vmss-autoscale-web
azd env select az104-m08-vmss
azd env refresh
$Url = (azd env get-value DEMO_URL).Trim()
$Rg = (azd env get-value AZURE_RESOURCE_GROUP).Trim()
$Vmss = "vmss-demo"
```

No necesitas azd up para empezar cada clase si los recursos ya están desplegados. Volver a provisionar reaplica capacidad inicial uno y autoscaling habilitado.

## 5 Mostrar las reglas y preparar el portal

El perfil tiene mínimo uno, inicial uno y máximo dos. Aumenta una VM si CPU promedio es mayor a 60 durante cinco minutos; reduce una VM si es menor a 25 durante cinco minutos. Cooldown de cinco minutos en ambas reglas. La ventana de cinco minutos es de evaluación, no una promesa de creación inmediata.

```powershell
az monitor autoscale show -g $Rg -n auto-web --output json
az monitor autoscale rule list -g $Rg --autoscale-name auto-web --output json
```

En Azure Portal abre rg-az104-m08-vmss → vmss-demo. Deja tres pestañas: Métricas con Percentage CPU, Average y granularidad de un minuto; Instancias; e historial de ejecución de Escalado. También puedes localizar auto-web desde Azure Monitor → Autoscale. Los nombres del menú dependen del idioma y pueden cambiar.

Antes de comenzar verifica una instancia, web saludable y CPU baja. Lleva el despliegue preparado para que el tiempo de clase se concentre en provocar y observar el escalado.

## Qué decir

“Ustedes generan cálculos reales en el servidor. El script que ejecutaré representa más usuarios y usa la misma aplicación. Si la CPU promedio supera el umbral el tiempo suficiente, Azure agrega una VM sin que cambiemos manualmente el número de instancias.”

“azd organiza el entorno y el despliegue. Bicep describe los recursos. Azure Monitor decide cuándo escalar. El balanceador dirige las conexiones hacia las VMs saludables.”

## 6 Participación de los alumnos y carga del instructor

Comparte $Url con los siete alumnos. Primero pide Generar trabajo una vez: deben ver el nombre del servidor y el tiempo del cálculo. Luego pide Participar continuamente. Cada navegador mantiene una solicitud a la vez, con una pausa corta antes de repetir.

La portada es liviana; el endpoint /work ejecuta un cálculo PBKDF2 para consumir CPU. La aplicación limita a ocho cálculos concurrentes por VM. Bajo saturación puede responder 429; los clientes vuelven a intentar. Detener mi participación evita solicitudes nuevas y deja terminar la que ya está en curso.

Abre una segunda terminal en la raíz del proyecto para simular usuarios adicionales. Este script genera solicitudes al mismo /work, desactiva keep-alive para abrir conexiones nuevas y termina automáticamente después del plazo indicado.

```powershell
Set-Location C:\GithubOrden\training-templates\AZ-104\module-08-virtual-machines\demos\demo-01-vmss-autoscale-web
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$Url = (azd env get-value DEMO_URL).Trim()
.\scripts\Carga-Web.ps1 -Url $Url -Clientes 12 -Minutos 15
```

Observa CPU en el portal. Si no supera 60 de manera sostenida, detén el generador con Ctrl+C y prueba 20 clientes. El script admite hasta 32 clientes y 30 minutos. Si /work no responde, diagnostica conectividad antes de aumentar carga.

```powershell
.\scripts\Carga-Web.ps1 -Url $Url -Clientes 20 -Minutos 15
```

## Qué decir bajo carga

“Los cálculos compiten por la CPU y pueden tardar más. Azure mira el promedio en una ventana reciente. La regla necesita carga sostenida, no un único pico.”

## 7 Observar el aumento y ambos servidores

Mantén alumnos y script generando carga. Muestra el aumento de CPU, una ejecución de autoscaling y la segunda instancia. Puedes consultar el estado desde la primera terminal sin detener el generador.

```powershell
az vmss list-instances -g $Rg -n $Vmss `
  --query "[].{Id:instanceId,Nombre:osProfile.computerName,Estado:provisioningState}" `
  --output table
```

La nueva instancia recibe la aplicación mediante cloud-init. El balanceador espera a que /health responda antes de dirigirle solicitudes. La ventana de cinco minutos se suma a evaluación, publicación de métricas, arranque de VM y sondas. Ensaya los tiempos reales; reserva 10 a 15 minutos para observar el aumento.

Cuando las dos VMs estén listas, realiza nuevas conexiones para facilitar respuestas de ambos servidores.

```powershell
1..20 | ForEach-Object {
  curl.exe -sS --http1.1 -H "Connection: close" `
    --connect-timeout 5 --max-time 30 "$Url/work"
  Write-Host ""
  Start-Sleep -Milliseconds 300
}
```

No esperes alternancia estricta: el balanceador distribuye flujos y un navegador puede reutilizar conexión. La evidencia principal es el historial de autoscaling y las dos instancias. El promedio de CPU puede bajar al agregar capacidad; el balanceador reparte trabajo nuevo, no migra cálculos que ya empezaron.

## Qué decir al aparecer la segunda VM

“No pulsamos aumentar capacidad. La regla reaccionó a la carga. Bicep definió cómo debe ser la nueva VM y Azure la creó con la misma web. Ahora las conexiones nuevas pueden llegar a ambos servidores.”

## 8 Detener la carga y mostrar la reducción

Pide a todos los alumnos pulsar Detener mi participación y cerrar la página si hace falta. En la terminal del generador pulsa Ctrl+C. Detén también cualquier bucle de solicitudes. Las solicitudes en curso pueden tardar un poco en terminar.

Si se interrumpió la terminal del generador inesperadamente, revisa sus jobs. Ejecuta este bloque únicamente en la terminal dedicada al generador, ya que detiene sus jobs.

```powershell
Get-Job
Get-Job | Stop-Job
Get-Job | Remove-Job -Force
```

Observa CPU baja. Después de promedio menor a 25 por cinco minutos, cooldown y comprobaciones de estabilidad, Azure puede reducir a una VM. La reducción tampoco ocurre instantáneamente.

```powershell
az vmss list-instances -g $Rg -n $Vmss --output table
curl.exe --max-time 10 "$Url/health"
```

## Qué decir

“Terminó la demanda y ya no necesitamos dos máquinas. La regla reduce capacidad hasta el mínimo configurado. La web continúa funcionando en la instancia que queda.”

Si no reduce, comprueba usuarios activos, jobs, CPU promedio, mínimo uno e historial por cooldown o prevención de oscilaciones. Para demostrar reducción automática, espera la regla y evita cambiar capacidad manualmente durante esta parte.

## 9 Reiniciar la demo y terminar el uso

Para otro ensayo, detén toda carga y usa este bloque. Es un reinicio manual del estado inicial y debes distinguirlo del escalado automático que mostraste.

```powershell
az monitor autoscale update -g $Rg -n auto-web --enabled false
az vmss scale -g $Rg -n $Vmss --new-capacity 1
az vmss list-instances -g $Rg -n $Vmss --output table
az monitor autoscale update -g $Rg -n auto-web --enabled true
```

Espera a que exista un intervalo reciente de CPU baja antes de repetir. No necesitas redesplegar. Si cambias la infraestructura, azd provision la reaplica; revisa antes que no haya una demostración activa.

## Eliminar el entorno con azd

Cuando termines, detén solicitudes y selecciona el entorno correcto. Consulta su grupo y recursos antes de confirmar la eliminación. azd down elimina el entorno desplegado que administra este proyecto. El grupo de los demos anteriores, si existe con otro nombre, se conserva y puede seguir generando costos.

```powershell
azd env select az104-m08-vmss
$Rg = (azd env get-value AZURE_RESOURCE_GROUP).Trim()
az resource list -g $Rg --output table
azd down
```

Revisa la lista y la confirmación de azd antes de aceptarla. No uses --force en el primer ensayo: comprueba qué se eliminará. Volver a una sola VM reduce consumo pero no elimina costos del entorno.

## Guion de 40 minutos

Cinco minutos de arquitectura y reglas; cinco de participación; quince de carga y aumento; cinco para observar ambos servidores; diez para detener y observar reducción. Deja el proyecto desplegado y ensayado antes de clase. Si la reducción tarda más, continúa el repaso mientras Azure evalúa.

## 10 Archivos y solución de problemas

azure.yaml define la raíz de infraestructura. main.bicep trabaja a nivel de suscripción y crea el grupo con etiqueta azd-env-name. web.bicep trabaja a nivel de grupo y contiene los seis recursos principales. main.parameters.json recibe entorno, ubicación, clave pública y tamaño.

cloud-init.yaml define la instalación del Python de app.py y el servicio systemd. app.py es la fuente del backend; Bicep la inserta como base64 dentro de cloud-init al compilar. Editarla no actualiza las instancias ya creadas. Si modificas cloud-init, el contenido nuevo es para la configuración de futuras instancias y no actualiza automáticamente las existentes.

- azd no encuentra proyecto: vuelve a la carpeta donde está azure.yaml.

- Falta SSH_PUBLIC_KEY: selecciona el entorno y ejecuta Preparar-Clave.ps1.

- Falta DEMO_URL: comprueba éxito de provision y ejecuta azd env refresh.

- Falla por región: verifica AZURE_LOCATION en el entorno; esta plantilla pasa la misma región al grupo y al módulo, sin ubicaciones adicionales.

- Falla por cuota: revisa vCPU regionales y de familia, y el máximo de dos instancias.

- No sube CPU: verifica /work y el script; evita tamaños B y aumenta clientes con prudencia hasta 20.

- VM nueva sin web: revisa cloud-init, systemd y la sonda con Run Command sobre su instanceId.

- CPU alta pero no escala: revisa promedio sostenido, autoscaling habilitado, historial, cuota y cooldown.

## Documentación de referencia

https://learn.microsoft.com/azure/developer/azure-developer-cli/azd-schema

https://learn.microsoft.com/azure/developer/azure-developer-cli/manage-environment-variables

https://learn.microsoft.com/azure/developer/azure-developer-cli/reference

https://learn.microsoft.com/azure/virtual-machine-scale-sets/tutorial-autoscale-cli
