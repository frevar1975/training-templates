# Demo 02 · Test Failover con Azure Site Recovery

## Objetivo

Replicar una VM Windows con IIS desde Central US a West US 2, ejecutar un Test Failover en una red aislada y demostrar que la aplicación funciona en la VM temporal, sin mover producción.

## Topología probada

| Elemento | Valor |
|---|---|
| VM origen | `vm-asr-demo` |
| Grupo de recursos origen | `rg-az104-asr-demo` |
| Región origen | Central US (`centralus`) |
| Red origen | `vnet-asr-source`, subred `snet-asr-source` (`10.20.1.0/24`) |
| Recovery Services vault | `rsv-az104-asr-demo` |
| Grupo de recursos del vault | `rg-az104-asr-vault` |
| Región de destino | West US 2 (`westus2`) |
| Grupo de recursos destino | `rg-az104-asr-demo-1` |
| Red aislada de prueba | `vnet-asr-test-west`, subred `snet-asr-test` (`10.30.1.0/24`) |
| Tamaño | `Standard_B2s` |

Los nombres son ejemplos. No reutilices un grupo que todavía esté en estado **Deleting**. Comprueba también que los prefijos de red estén libres y no se superpongan con redes conectadas.

## 1. Preparar PowerShell y Azure CLI

Abre Windows PowerShell o PowerShell 7. No copies el prompt `PS C:\...>`. En Windows PowerShell 5.1, ejecuta los comandos en líneas separadas y usa el acento grave para continuar líneas; no uses `&&`.

```powershell
az login
$subscriptionId = Read-Host "ID de la suscripcion de Azure"
az account set --subscription $subscriptionId
az account show --query "{Suscripcion:name,Id:id}" --output table

$rg = "rg-az104-asr-demo"
$location = "centralus"
$vnetName = "vnet-asr-source"
$subnetName = "snet-asr-source"
$nsgName = "nsg-asr-source"
$vmName = "vm-asr-demo"
$vaultRg = "rg-az104-asr-vault"
$vaultName = "rsv-az104-asr-demo"
$myPublicIp = (Invoke-RestMethod -Uri "https://api.ipify.org").Trim()
```

Confirma la suscripción activa. Si cambias de red, vuelve a consultar tu IP pública antes de crear las reglas NSG.

## 2. Crear la VM de origen

Crea el grupo y la red. Si el grupo ya existe, verifica que corresponda a este demo y no ejecutes una eliminación automática.

```powershell
az group create --name $rg --location $location --output table

az network vnet create `
  --resource-group $rg `
  --name $vnetName `
  --location $location `
  --address-prefixes 10.20.0.0/16 `
  --subnet-name $subnetName `
  --subnet-prefixes 10.20.1.0/24 `
  --output table

az network nsg create `
  --resource-group $rg `
  --name $nsgName `
  --location $location `
  --output none

az network nsg rule create `
  --resource-group $rg `
  --nsg-name $nsgName `
  --name "Allow-RDP-MyIP" `
  --priority 1000 `
  --direction Inbound `
  --access Allow `
  --protocol Tcp `
  --source-address-prefixes "$myPublicIp/32" `
  --source-port-ranges "*" `
  --destination-address-prefixes "*" `
  --destination-port-ranges 3389 `
  --output none
```

Consulta el SKU en el destino antes del despliegue:

```powershell
az vm list-skus `
  --location westus2 `
  --resource-type virtualMachines `
  --query "[?name=='Standard_B2s'].{Tamano:name,Restricciones:restrictions}" `
  --output json
```

Crea la VM usando el URN completo de imagen. En la sesión, el alias `Win2022AzureEdition` dio ResourceNotFound. Pasa a `--subnet` el ID completo de la subred; al pasar solo el nombre, Azure CLI intentó crear un prefijo por defecto incompatible.

```powershell
$subnetId = az network vnet subnet show `
  --resource-group $rg `
  --vnet-name $vnetName `
  --name $subnetName `
  --query id `
  --output tsv

az vm create `
  --resource-group $rg `
  --name $vmName `
  --location $location `
  --image "MicrosoftWindowsServer:WindowsServer:2022-datacenter-azure-edition:latest" `
  --size Standard_B2s `
  --admin-username azureadmin `
  --storage-sku StandardSSD_LRS `
  --subnet $subnetId `
  --nsg $nsgName `
  --nsg-rule NONE `
  --public-ip-sku Standard `
  --output table
```

Azure solicitará la contraseña de administrador de forma interactiva. Usa una contraseña segura y no la pongas en scripts ni en Git.

## 3. Instalar IIS y publicar la página

Instala el rol con Run Command:

```powershell
az vm run-command invoke `
  --resource-group $rg `
  --name $vmName `
  --command-id RunPowerShellScript `
  --scripts "Install-WindowsFeature -Name Web-Server -IncludeManagementTools" `
  --output json
```

Añade una regla HTTP restringida a tu IP:

```powershell
az network nsg rule create `
  --resource-group $rg `
  --nsg-name $nsgName `
  --name "Allow-HTTP-MyIP" `
  --priority 1010 `
  --direction Inbound `
  --access Allow `
  --protocol Tcp `
  --source-address-prefixes "$myPublicIp/32" `
  --source-port-ranges "*" `
  --destination-address-prefixes "*" `
  --destination-port-ranges 80 `
  --output none
```

Escribe la página y verifica que IIS esté activo. El comando de una sola línea fue el que funcionó de forma reproducible en la sesión:

```powershell
az vm run-command invoke `
  --resource-group $rg `
  --name $vmName `
  --command-id RunPowerShellScript `
  --scripts "Set-Content -Path 'C:\inetpub\wwwroot\index.html' -Value '<html><body style=''font-family:Segoe UI;text-align:center;margin-top:10%''><h1>Aplicacion de demostracion</h1><h2>VM de origen: vm-asr-demo</h2><p>Region primaria: Central US</p><p>Demo de Azure Site Recovery</p></body></html>' -Encoding UTF8; Get-Service W3SVC | Select-Object Name,Status; Test-Path 'C:\inetpub\wwwroot\index.html'; Get-Content 'C:\inetpub\wwwroot\index.html'" `
  --output json
```

Obtén la IP y comprueba desde tu PC que la página responde con HTTP 200:

```powershell
$publicIp = az vm show --resource-group $rg --name $vmName --show-details --query publicIps --output tsv
Invoke-WebRequest -Uri "http://$publicIp" -UseBasicParsing |
  Select-Object StatusCode, StatusDescription
```

## 4. Crear el vault y la red de prueba

El vault se creó en East US, separado del grupo de la VM. La replicación se configuró desde la experiencia de Site Recovery del vault.

```powershell
az group create --name $vaultRg --location eastus --output table
az backup vault create --resource-group $vaultRg --name $vaultName --location eastus --output table
```

En el portal, comprueba o crea el grupo destino `rg-az104-asr-demo-1` en West US 2 y la VNet de prueba `vnet-asr-test-west`. Se usaron `10.30.0.0/16` para la VNet y `10.30.1.0/24` para `snet-asr-test`. Esta red debe quedar aislada de la red origen.

## 5. Habilitar replicación

En Azure Portal:

1. Abre el vault `rsv-az104-asr-demo` y entra a **Site Recovery**.
2. Habilita replicación para `vm-asr-demo` en `rg-az104-asr-demo`, origen Central US.
3. Selecciona destino West US 2.
4. Configura como grupo de recursos destino `rg-az104-asr-demo-1`.
5. Mantén tamaño destino `Standard_B2s`.
6. Selecciona `vnet-asr-test-west` y `snet-asr-test` como red de Test Failover.
7. Usa la política `24-hour-retention-policy`; no hace falta un grupo multi-VM para esta VM individual.
8. Revisa el resumen y habilita la replicación.

Espera a que **Replication Health** indique **Healthy** y **Status** sea **Protected** antes de ejecutar la prueba. La sincronización inicial puede superar una hora según la VM, la región y el estado del servicio.

## 6. Ejecutar Test Failover

1. En **Replicated items**, abre `vm-asr-demo` y selecciona **Test failover**.
2. Elige el recovery point **Latest processed (lowest RTO)**.
3. Selecciona `vnet-asr-test-west` como red aislada.
4. Ejecuta la comprobación de requisitos previos. Continúa solo si es correcta.
5. Inicia Test Failover y espera el trabajo hasta que terminen las fases de creación y arranque.

En la sesión, la VM temporal quedó **Running** en West US 2, con IP privada en la subred de prueba, sin IP pública, y el job terminó correctamente.

## 7. Validar la aplicación recuperada

En el portal, abre la VM temporal creada en `rg-az104-asr-demo-1`. Usa **Operations > Run command > RunPowerShellScript**:

```powershell
Get-Service W3SVC | Select-Object Name,Status
Test-Path 'C:\inetpub\wwwroot\index.html'
Get-Content 'C:\inetpub\wwwroot\index.html'
```

Resultado observado: servicio IIS `Running`, archivo existente (`True`) y contenido HTML de la demo. La VM de prueba no requiere IP pública: la validación se hace con Run Command. La propiedad **Active location** de la VM protegida debe seguir indicando Central US.

## 8. Limpiar Test Failover

En el elemento replicado original, selecciona **Cleanup test failover**, escribe una nota si el portal la solicita y confirma. Espera a que termine la limpieza y comprueba que la VM temporal haya sido eliminada y que el estado vuelva a **Protected** con salud **Healthy**.

No selecciones **Failover**, **Commit** ni **Disable replication** para cerrar un simulacro. Son acciones diferentes y pueden cambiar o detener la protección real.

## Evidencias y preguntas

- Estado inicial **Protected / Healthy** y región activa Central US.
- Job Test Failover con todas sus tareas en **Successful**.
- VM temporal en West US 2, sin IP pública, en la VNet aislada.
- IIS activo, HTML presente y contenido legible desde Run Command.
- Limpieza del simulacro completada y VM origen nuevamente protegida.

Preguntas: ¿qué diferencia hay entre Azure Backup y Site Recovery? ¿Por qué probar una red aislada? ¿Qué evidencia demuestra que la VM recuperada arrancó con los datos replicados? ¿Por qué el estado **Protected** no sustituye una prueba de recuperación?
