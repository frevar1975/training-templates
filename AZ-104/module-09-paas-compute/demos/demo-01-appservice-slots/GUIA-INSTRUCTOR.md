# AZ-104 · Plantilla reutilizable · App Service slots

## Objetivo y alcance
Una tienda azul V1 calcula correctamente un descuento de 20% desde Bs 500. La tienda verde V2 contiene un defecto deliberado: aplica 10%. Se publica V2 mediante un swap del slot staging a producción y se recupera V1 con un segundo swap. No hay pagos reales, pedidos persistentes ni base de datos.

Azure crea un grupo independiente, un App Service Plan Linux Standard S1, una Web App y un slot staging. Ambos slots comparten el plan y sus recursos. No se crea autoscaling ni VMSS en este laboratorio. S1 tiene consumo mientras el plan exista; no cambiar a F1 o B1 porque no soportan slots.

## Uso en cualquier edición
Esta carpeta es la fuente reutilizable del laboratorio. Elegir un nombre de entorno azd propio por curso o grupo, por ejemplo `az104-m09-certero-20261014`, y sustituir `az104-m09-slots` en todos los comandos de creación, selección y limpieza. El grupo será `rg-<nombre-del-entorno>`. Elegir suscripción y región con cuota S1. No subir .azure, credenciales ni URLs generadas.

## 1. Preparar las herramientas
Usar PowerShell 7 en Windows Terminal. No hace falta Node.js local para desplegar: las aplicaciones no tienen dependencias externas y se ejecutan en Azure.

```powershell
winget install --exact --id Microsoft.PowerShell
winget install --exact --id Microsoft.Azd
winget install --exact --id Microsoft.AzureCLI
```
Cerrar y abrir Windows Terminal, seleccionar PowerShell 7. Verificar:

```powershell
$PSVersionTable.PSVersion
azd version
az version
```
Si ya están instaladas, solo verificar.

## 2. Extraer el proyecto
Descomprimir el ZIP en `C:\clases`. Debe quedar `C:\clases\az104_mod09_slots\azure.yaml`.

```powershell
cd C:\clases\az104_mod09_slots
Get-ChildItem
```
No ejecutar azd init: la plantilla ya está incluida.

## 3. Seleccionar la suscripción
```powershell
azd auth login
az login
az account list --query "[].{Nombre:name,Id:id,Predeterminada:isDefault}" --output table
```
Copiar el ID de la suscripción que tiene cuota S1. No asumir que es la misma del VMSS: puede ser necesario utilizar otra suscripción.

```powershell
$SubscriptionId = "PEGAR-ID-DE-SUSCRIPCION"
az account set --subscription $SubscriptionId
azd env new az104-m09-slots
azd env set AZURE_SUBSCRIPTION_ID $SubscriptionId
azd env set AZURE_LOCATION eastus2
```
Si el entorno ya existe, usar `azd env select az104-m09-slots` en lugar de `azd env new`.

## 4. Crear recursos y publicar V1/V2
Si Windows bloquea scripts descargados, ejecutar en la misma terminal:

```powershell
Get-ChildItem .\scripts\*.ps1 | Unblock-File
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
```
El ajuste de ejecución aplica solo a la sesión actual. Las políticas de dominio tienen precedencia.

```powershell
azd up
```
Aceptar la ejecución de hooks si azd lo solicita. El preflight verifica acceso de Azure CLI y disponibilidad del runtime. Bicep crea el grupo y los recursos. El hook postprovision comprime el contenido de cada versión y usa Azure CLI para publicarlo: V1 en producción y V2 en staging. Después consulta las URLs para confirmar las versiones.

Esperar el resultado completo. La primera publicación puede tardar varios minutos. El despliegue no realiza swaps.

## 5. Abrir y comprobar
```powershell
$Prod = (azd env get-value PRODUCTION_URL).Trim()
$Stage = (azd env get-value STAGING_URL).Trim()
$App = (azd env get-value WEBAPP_NAME).Trim()
$Rg = (azd env get-value AZURE_RESOURCE_GROUP).Trim()
Start-Process $Prod
Start-Process $Stage
.\scripts\Verificar.ps1 | Format-Table -AutoSize
```
Resultado inicial:

| URL | Versión | Color | 2 audífonos de Bs 300 |
|---|---|---|---|
| Producción | 1.0 | Azul | Subtotal 600, descuento 120, total 480 |
| Staging | 2.0 | Verde | Subtotal 600, descuento 60, total 540 |

Ambas deben estar disponibles antes de la clase. La sonda /health comprueba que el proceso responda; no descubre el defecto comercial. Ese contraste es parte de la enseñanza.

## 6. Guion de clase: situación inicial
Compartir únicamente la URL de producción con los alumnos. Seleccionar Audífonos inalámbricos, cantidad 2 y Calcular total. Pedirles anotar Bs 480.

Qué decir: “Tenemos una aplicación web administrada por Azure. No instalamos el sistema operativo. El plan define la capacidad; la Web App contiene nuestra aplicación”.

En Azure Portal buscar el nombre contenido en $App. Abrir la Web App. Desde Overview pulsar el vínculo del App Service Plan y mostrar Standard S1. Volver a la Web App.

## 7. Mostrar ensayo
En el menú de la Web App buscar Deployment slots / Ranuras de implementación. Mostrar producción y staging. Abrir staging y Browse / Examinar, o usar $Stage. Mostrar el color verde y versión 2.0.

Qué decir: “El slot es una aplicación activa con otra dirección. Podemos probar la nueva versión sin reemplazar todavía producción”.

Para la narración del incidente, mostrar primero una compra pequeña: mouse, cantidad 1, total Bs 100. Explicar que esta prueba superficial pasa. El ensayo ya validó por separado el defecto conocido; no estamos recomendando omitir validaciones en producción real.

## 8. Publicar con Swap
Desde Deployment slots en la Web App principal pulsar Swap / Intercambiar. Fuente: staging. Destino: production. Revisar la pantalla y confirmar el intercambio. Esperar la finalización en Notifications / Notificaciones.

No usar “Swap with preview” para este ensayo. No iniciar un segundo swap mientras el primero siga en curso.

En producción refrescar la página: debe verse verde y V2. El hostname de producción no cambia. Los alumnos deben refrescar: una página ya abierta no cambia mágicamente.

Qué decir: “Publicamos el código que estaba en staging usando la misma URL pública. La versión anterior queda en staging para una recuperación”.

## 9. Revelar el defecto
En producción seleccionar audífonos, cantidad 2. Subtotal Bs 600. La promoción anuncia 20%, pero el descuento es Bs 60 y el total Bs 540. Preguntar cuánto debería ser: Bs 480.

Qué decir: “La aplicación responde y la sonda dice saludable, pero una regla de negocio está mal. Disponibilidad técnica no equivale a comportamiento correcto”.

## 10. Recuperar V1
Volver a Deployment slots y ejecutar otro Swap: fuente staging, destino production. Ahora staging contiene V1. Esperar a que termine.

Refrescar producción: azul, V1, total Bs 480. Staging vuelve a quedar verde, V2, total Bs 540.

```powershell
.\scripts\Verificar.ps1 | Format-Table -AutoSize
```
Qué decir: “Recuperamos la versión anterior del código. Si hubiéramos cambiado una base de datos, el swap no desharía automáticamente esos cambios”.

El intercambio no garantiza ausencia absoluta de fallas en cualquier aplicación; aquí no hay sesiones ni persistencia y usamos procesos simples. No ejecutar azd up durante los swaps: el postprovision vuelve a publicar V1/V2.

## 11. Recuperar una publicación fallida o restablecer el ensayo
Si la infraestructura quedó creada pero un ZIP falló:

```powershell
.\scripts\Publicar-Versiones.ps1
```
Este comando sobrescribe ambas versiones y restablece el punto de partida. Ejecutarlo fuera de la demostración. Para errores 502/503 revisar Web App > Log stream y también el slot staging. Esperar el arranque y revisar /health.

Si el error es cuota Standard/S1 de Microsoft.Web: revisar la suscripción/región disponibles para App Service o solicitar cuota. F1 no resuelve este laboratorio porque no tiene slots. No eliminar recursos de otros demos para intentar resolverlo sin verificar la causa.

Si el recurso o deployment falla, no continuar a los swaps hasta comprobar las dos URLs.

## 12. Eliminar solo este laboratorio
```powershell
cd C:\clases\az104_mod09_slots
azd env select az104-m09-slots
azd env get-value AZURE_RESOURCE_GROUP
azd down
```
Confirmar únicamente si el grupo mostrado es `rg-az104-m09-slots`. Si no hay otros recursos añadidos manualmente allí, la limpieza no afecta al VMSS ni al servidor Arc de los otros grupos.

## 13. Prueba adicional: tráfico 50/50
Con producción V1 y staging V2: Web App > Deployment slots > Traffic %, asignar 50% a staging y guardar. Abrir la URL de producción desde diferentes dispositivos o navegadores independientes. La cookie mantiene la asignación: refrescar no garantiza alternancia. Al terminar devolver staging a 0% y guardar. Para garantizar producción en una sesión que conserve afinidad a staging, abrir la URL de producción con `?x-ms-routing-name=self`.

## Validación del ensayo
Ensayo del instructor realizado el 13 de octubre de 2026 en eastus2: azd up terminó correctamente; producción V1 devolvió subtotal 600, descuento 120 y total 480; staging V2 devolvió subtotal 600, descuento 60 y total 540. Instructor confirmó swap, recuperación y distribución de tráfico. Una suscripción con cuota S1 cero falló en validación; otra suscripción permitió el despliegue. No se guardan IDs de suscripción, estado .azure ni credenciales en GitHub.
