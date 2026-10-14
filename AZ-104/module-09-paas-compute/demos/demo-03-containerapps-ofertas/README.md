# AZ-104 · Modulo 9 · Container Apps: hora de ofertas

Demo complementario al laboratorio de Container Apps. Una tienda ficticia muestra la replica que responde; la clase genera solicitudes, se observa el escalado y se retira el trafico para observar cero replicas. No incluye pagos, base de datos ni registro de clientes.

## Preparacion y despliegue en Windows
Requisitos: Git, Azure CLI y azd. Los scripts usan PowerShell y Start-Job, compatible con Windows PowerShell 5.1 y PowerShell 7. No requiere Docker local, cuenta Docker Hub ni ACR. La imagen de desarrollo MCR es mayor que una imagen minima. El codigo se incorpora en Bicep para simplificar el lab; en produccion construir una imagen propia versionada.

Entrar a la carpeta de este demo (contiene azure.yaml). No usar azd init.

```powershell
azd auth login
az login
$SubscriptionId = "<ID-DE-TU-SUSCRIPCION>"
az account set --subscription $SubscriptionId
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az extension add --name containerapp --upgrade
azd env new az104-m09-containerapps
azd env set AZURE_SUBSCRIPTION_ID $SubscriptionId
azd env set AZURE_LOCATION eastus2
az bicep build --file .\infra\main.bicep
```
Si la compilacion falla, detenerse y resolver el error. Si pasa:

```powershell
azd up
Get-ChildItem .\scripts\*.ps1 | Unblock-File
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\Verificar.ps1
.\scripts\Obtener-Url.ps1
```
Creara rg-az104-m09-containerapps, entorno Consumption, Log Analytics y ca-ofertas-... con HTTPS, 0 a 3 replicas, 0,5 vCPU/1 GiB por replica y regla HTTP concurrentRequests=2. Los valores decimales Bicep usan json('0.5'). App Service y ACI anteriores no se modifican.

## 1. Despertar la tienda (3 minutos)
Mostrar la URL y pulsar Consultar oferta. La pagina no consulta automaticamente al abrir: el boton muestra que replica responde. La primera navegacion desde cero puede tardar por arranque y descarga de imagen. Si hay error transitorio, reintentar; no prometer un tiempo fijo.

Que decir: “Podemos dejar el minimo en cero. Una solicitud activa capacidad para atender a nuestros usuarios. Si necesitara respuesta mas predecible, usaria un minimo de uno o mas”.

## 2. Campana con los alumnos (5 a 8 minutos)
Compartir la URL. Pedir que pulsen Participar 2 minutos. Cada navegador crea dos ciclos de solicitudes limitados a dos minutos; no es necesario refrescar manualmente. Se espera un segundo en cada oferta para simular una operacion, sin prueba intensa de CPU. Una pagina abierta sin participar no produce carga continua.

El instructor puede mantener carga reproducible desde otra terminal:

```powershell
.\scripts\Carga-Web.ps1 -Clientes 16 -Minutos 5
```
Mientras corre, en una segunda terminal dentro del demo:

```powershell
.\scripts\Verificar.ps1
```
Repetir la consulta cada 20 a 30 segundos. En portal: Resource groups > rg-az104-m09-containerapps > ca-ofertas-... > Revisions and replicas; expandir la revision activa y observar replicas. Tambien Monitoring > Metrics > Replica Count, si aparece con ese nombre; usar ventana reciente y refrescar. Las metricas pueden tener retraso. Revisar Scale para ver minimo 0, maximo 3 y regla HTTP.

Que decir: “El numero maximo es un limite, no una cantidad garantizada. Azure calcula la demanda y ajusta replicas. No es una VM nueva por cada visitante”.

El contador de la pagina representa respuestas observadas en ESE navegador, no inventario Azure ni ventas persistentes. La distribucion no garantiza alternancia: comprobar el numero real con el portal y Verificar.ps1. Si la carga no provoca aumento tras varios minutos, comprobar cuota, replicas pendientes, logs y regla; despues probar 24 clientes por 5 minutos. No aumentar el limite de tres sin revisar cuota.

## 3. Retirar trafico y volver a cero (reservar 5 a 10 minutos)
Esperar que termine Carga-Web.ps1 o Ctrl+C. Pedir Detener a todos los alumnos y cerrar paginas. No consultar la oferta ni refrescar la web: esas solicitudes pueden evitar el descenso a cero. La pagina no mantiene un sondeo de fondo cuando esta inactiva. Puede quedar una solicitud en curso al detenerla.

Consultar solo el plano de administracion:

```powershell
.\scripts\Verificar.ps1
```
La lista de replicas de la revision debe finalmente estar vacia ([]). No prometer cero instantaneo: hay periodos de estabilizacion y enfriamiento. Si no baja, comprobar que no hay carga, monitores HTTP o pestañas participantes. Los health probes no equivalen a visitantes generando ofertas.

Que decir: “La demanda termino. La aplicacion y su URL siguen configuradas, pero no mantenemos replicas de computo activas”.

Abrir otra vez la URL para demostrar el arranque desde cero. El identificador de replica puede cambiar.

## Diferencia con demos anteriores
- VMSS: escalamos maquinas virtuales por CPU, administrando sistema y app.
- App Service slots: promovemos y revertimos versiones con swap.
- ACI: ejecutamos un trabajo y termina; Azure Files conserva resultados.
- Container Apps: servicio HTTP con replicas segun demanda, incluida escala a cero.

## Logs y diagnostico
```powershell
$Rg = (azd env get-value AZURE_RESOURCE_GROUP).Trim()
$App = (azd env get-value CONTAINER_APP_NAME).Trim()
$Sub = (azd env get-value AZURE_SUBSCRIPTION_ID).Trim()
az containerapp logs show --subscription $Sub -g $Rg -n $App --type system --tail 30
```
Si hay replicas, tambien --type console --container tienda. Los logs contienen replica y solicitud; no datos personales. Imagen MCR no evita fallos de conectividad o capacidad. Cuota Consumption es independiente de S1/ACI. Si no hay revision lista revisar eventos, imagen, puerto 8080 y probes. No cambiar region de un grupo existente; para otra region crear otro entorno.

## Costos y limpieza
El consumo de app depende de ejecucion y solicitudes. Escalar a cero no elimina los recursos ni todo posible costo: Log Analytics y retencion de logs pueden cobrar. No se garantiza costo cero. Descargar lo necesario antes de limpiar.

```powershell
azd env select az104-m09-containerapps
azd env get-value AZURE_RESOURCE_GROUP
azd down
```
Confirmar que el grupo es el de ESTE demo.

## Validacion
Preparado para ensayo: servidor probado localmente, endpoints de salud/oferta, identificador de replica y solicitudes simultaneas. Infraestructura Bicep y scripts PowerShell pendientes de compilacion y ejecucion en Windows/Azure. El escalado real, arranque desde cero, cuota, portal y vuelta a cero deben validarse con el instructor antes de marcar como demo probado.

## Referencias
https://learn.microsoft.com/azure/container-apps/scale-app
https://learn.microsoft.com/azure/templates/microsoft.app/2024-03-01/containerapps
https://learn.microsoft.com/azure/templates/microsoft.app/2024-03-01/managedenvironments
