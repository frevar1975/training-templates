# AZ-104 · Módulo 9 · ACI: un reporte sin servidor permanente

## Resultado
Un contenedor Linux procesa ventas ficticias, genera un reporte HTML con indicadores y comparaciones, lo guarda en Azure Files y termina con exit code 0. El CSV y el historial sobreviven al proceso. Se vuelve a ejecutar con una venta adicional y cambia el resultado. No hay una web pública ni pagos.

Es complemento del lab 09b: demuestra un trabajo por lotes, volumen persistente, logs y política Never, además de desplegar un contenedor.

## 1. Preparación
Abrir la carpeta de este demo, que contiene azure.yaml. Si se usa el ZIP, descomprimir en C:\clases\az104_mod09_aci_reportes. Si se usa GitHub, clonar el repositorio y entrar a la carpeta demos/demo-02-aci-reportes del módulo 9. Abrir Windows Terminal con PowerShell. Se requieren Azure CLI y azd. No se requiere Docker local ni Python local ni un registro privado.

```powershell
cd C:\clases\training-templates\AZ-104\module-09-paas-compute\demos\demo-02-aci-reportes
azd version
az version
azd auth login
az login
```
La imagen pública oficial Python se descarga de Docker Hub. El código y el CSV inicial se incorporan desde archivos del proyecto a la plantilla Bicep. Esta simplificación es para el laboratorio; en una implementación productiva se construiría una imagen propia versionada y se almacenaría en un registro como ACR.

## 2. Entorno independiente
Usar una suscripción con permisos para crear grupos y recursos de Storage/ACI. La suscripción que funcionó para S1 puede ser el primer ensayo, pero ACI tiene su propia cuota.

```powershell
$SubscriptionId = "<ID-DE-TU-SUSCRIPCION>"
az account set --subscription $SubscriptionId
azd env new az104-m09-aci
azd env set AZURE_SUBSCRIPTION_ID $SubscriptionId
azd env set AZURE_LOCATION eastus2
```
Si el entorno existe: azd env select az104-m09-aci. Para otro curso usar otro nombre en todos los comandos, incluida limpieza. No guardar .azure ni credenciales en GitHub.

Registrar los proveedores si no están registrados:

```powershell
az provider register --namespace Microsoft.ContainerInstance --wait
az provider register --namespace Microsoft.Storage --wait
```

## 3. Desplegar
```powershell
azd up
```
No ejecutar azd init. La plantilla crea:
- Grupo rg-az104-m09-aci.
- StorageV2 Standard LRS y recurso compartido reportes (cuota de 5 GiB; no es preasignación de archivos).
- Grupo aci-reportes-demo, un contenedor generador, 1 vCPU y 1,5 GB de memoria.
- Montaje /reports desde Azure Files.
- Política restartPolicy Never.

El contenedor empieza automáticamente en el primer despliegue. Tiene una pausa didáctica de 60 segundos, con mensajes cada 10 segundos, para que se vea en ejecución. Puede haber terminado cuando finalice azd up: eso es esperado. El éxito del aprovisionamiento no basta para validar el resultado del trabajo; revisar exit code y archivos.

El proceso consume recursos mientras se ejecuta. Al terminar se detiene la facturación de proceso aplicable al contenedor; Azure Files y sus operaciones siguen teniendo consumo. Para limpiar todos los recursos usar azd down.

## 4. Comprobación en terminal
```powershell
.\scripts\Verificar.ps1
```
Si Windows bloquea el script descargado:
```powershell
Get-ChildItem .\scripts\*.ps1 | Unblock-File
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\Verificar.ps1
```
Resultado: contenedor Terminated, salida 0, log Trabajo completado, total Bs 6,600.00. Running durante la pausa también es normal; esperar y repetir. Exit code distinto de 0 requiere diagnóstico antes de seguir.

## 5. Mostrar el proceso en Azure Portal
1. Abrir Resource groups > rg-az104-m09-aci.
2. Abrir aci-reportes-demo.
3. Entrar a Containers / Contenedores.
4. Seleccionar generador y mostrar Properties / Propiedades, Events / Eventos y Logs / Registros.
5. Si ya terminó, usar Restart / Reiniciar del grupo para repetirlo. Si Restart está deshabilitado y aparece Start / Iniciar, usar Start. Esperar y refrescar Logs durante la pausa.
6. Al finalizar revisar el estado del CONTENEDOR y exit code 0. El estado del grupo o del aprovisionamiento puede indicar Succeeded: no es lo mismo que el estado del proceso.

Qué decir: “No necesitamos una aplicación atendiendo las 24 horas. Este contenedor tiene una tarea: leer datos, generar archivos y terminar”.

Qué decir sobre Never: “Terminar con código cero es éxito. Never evita reiniciarlo automáticamente, aunque falle; para reintentar en este laboratorio lo iniciamos manualmente”.

No confundir este trabajo manual con una tarea programada. No hay programador incluido en la plantilla.

## 6. Abrir el reporte y demostrar persistencia
1. Volver al grupo de recursos.
2. Abrir la cuenta stacirep... (también la muestra Verificar.ps1).
3. Entrar a Data storage / Almacenamiento de datos > File shares / Recursos compartidos de archivos.
4. Abrir reportes > Browse / Examinar.
5. Ver ventas.csv, reporte-actual.html, reporte-<ejecución>.html y resumen-<ejecución>.json.
6. Seleccionar reporte-actual.html > Download / Descargar y abrirlo en Edge desde Descargas.
7. Mostrar total Bs 6.600, 32 unidades, 12 registros, sucursal líder Norte.
8. Mostrar ventas por sucursal: Centro 2.100, Norte 2.700, Sur 1.800.
9. Mostrar identificador y fecha UTC de ejecución al pie. La hora UTC difiere cuatro horas de Bolivia.
10. Volver al contenedor terminado, luego regresar a los archivos: el reporte sigue disponible.

No esperar que Azure Files publique una URL de sitio web. Se descarga el HTML y se abre localmente; es autocontenido, sin recursos externos. Acceder mediante clave de cuenta en el explorador de archivos del portal si solicita método de autorización y tu usuario tiene listKeys. No compartir ni copiar claves al material de clase. El montaje ACI usa la clave obtenida por Bicep, sin escribirla en el repositorio ni en las salidas.

Qué decir: “El cómputo terminó; el almacenamiento tiene un ciclo de vida independiente”.

## 7. Cambiar los datos y volver a ejecutar
Hacerlo con el contenedor terminado, para evitar editar mientras lee.

1. En reportes descargar ventas.csv.
2. Abrirlo con Bloc de notas para preservar encabezados y valores.
3. Agregar al final una nueva línea:

```csv
2026-10-07,Centro,Audifonos,1,300
```

4. Guardar como UTF-8, manteniendo el nombre ventas.csv.
5. En reportes pulsar Upload / Cargar, seleccionar ese archivo y confirmar sobreescritura. Si pide sobrescribir, aceptar únicamente ventas.csv.
6. Volver a aci-reportes-demo y usar Restart o Start según esté habilitado.
7. Observar los logs: “Usando ventas.csv existente”. Esperar la finalización.
8. Descargar nuevamente reporte-actual.html y abrir la descarga nueva (no el archivo anterior del navegador).
9. Resultado: Bs 6.900, 33 unidades, 13 registros. Centro sube a Bs 2.400; Norte sigue líder con Bs 2.700.
10. En reportes quedan los reportes de ejecuciones anteriores. El actual se sobrescribe, el historial no.

Qué decir: “Reutilizamos el mismo contenedor y procesamos nuevos datos. El archivo de entrada está fuera del contenedor y los resultados quedan registrados por ejecución”.

## 8. Prueba opcional: borrar solo el cómputo
Después de comprobar reportes y logs, en el recurso aci-reportes-demo usar Delete / Eliminar. Eliminar solo este recurso, no el grupo ni Storage. Volver al recurso compartido: los archivos siguen ahí. azd up puede recrear ACI; conservará el CSV modificado porque Storage no se borró. Reaplicar infraestructura puede volver a ejecutar el trabajo, por lo que no usarlo accidentalmente durante el guion.

Esta prueba es más clara que reiniciar: el contenedor dejó de existir y el reporte sigue disponible. No eliminar Storage si se quiere demostrar persistencia.

## 9. Diagnóstico
- Image pull / toomanyrequests: revisar Events. Docker Hub puede limitar descargas; no es una falla del script. Reintentar o preparar una imagen en ACR como variante después de validar el ensayo.
- Cuota/capacidad ACI: revisar el error de Microsoft.ContainerInstance. Elegir otra región con un entorno nuevo si hace falta; no cambiar la región de un grupo ya creado.
- Mount failure: revisar Events y que exista reportes, que la cuenta permita shared key y conectividad SMB. La plantilla usa Linux como root, requerido para este montaje.
- Exit code 1: leer los logs. CSV inválido falla explícitamente en lugar de generar un reporte incorrecto. El archivo anterior puede seguir existiendo: verificar fecha e identificador para no confundirlo con una ejecución nueva.
- Sin archivos: verificar estado de proceso y montaje; no usar solo ProvisioningState como evidencia.
- Si falta una salida de azd después de provision exitoso: azd env refresh.

## 10. Limpieza completa
```powershell
cd C:\clases\training-templates\AZ-104\module-09-paas-compute\demos\demo-02-aci-reportes
azd env select az104-m09-aci
azd env get-value AZURE_RESOURCE_GROUP
azd down
```
Confirmar que el grupo corresponde a este laboratorio. Esto elimina también Storage, entrada e historial. No usar antes de terminar la demostración de persistencia.

## Validación
Pruebas locales: CSV válido, totales por sucursal, valores inválidos, historial de dos ejecuciones, conservación del CSV y tercera ejecución con una venta nueva. Validación Azure del instructor (14/10/2026, eastus2): Bicep compiló tras representar la memoria decimal como json('1.5'); azd up completó en 1 min 23 s. El contenedor terminó con exit code 0, procesó 12 registros y 32 unidades por Bs 6.600 y confirmó la escritura de HTML/JSON en Azure Files. Pendientes: abrir el HTML descargado, probar Start/Restart, modificar el CSV y comprobar persistencia e historial.

## Referencias
https://learn.microsoft.com/azure/container-instances/container-instances-restart-policy
https://learn.microsoft.com/azure/container-instances/container-instances-volume-azure-files
https://learn.microsoft.com/azure/container-instances/container-instances-stop-start
