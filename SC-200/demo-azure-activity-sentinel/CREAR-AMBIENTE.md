# CREAR AMBIENTE — SC-200 | Microsoft Sentinel

Guía base para preparar un ambiente de Microsoft Sentinel desde cero usando Windows PowerShell 5.1 y Azure CLI. Ajusta los nombres si el curso usa otros recursos.

## Requisitos

- Azure CLI instalada.
- Permisos para seleccionar una suscripción, crear un grupo de recursos y crear un workspace de Log Analytics.
- Una suscripción de laboratorio activa. Log Analytics y Sentinel pueden generar cargos por ingestión y retención.

## 1. Iniciar sesión y seleccionar la suscripción

Si todavía no hay una sesión activa:

```powershell
az login
```

Selecciona la suscripción por su nombre visible. No copies ni publiques el identificador de la suscripción en el repositorio:

```powershell
$subscriptionName = "<NOMBRE_VISIBLE_DE_LA_SUSCRIPCION>"
az account set --subscription $subscriptionName
az account show --query "{Suscripcion:name,Estado:state,Tenant:tenantId}" -o table
```

Confirma que el estado sea `Enabled` y que el nombre corresponda a la suscripción del laboratorio. La consulta omite el ID de la suscripción.

## 2. Crear el grupo de recursos

```powershell
$resourceGroup = "rg-sc200"
$location = "eastus"

az group create --name $resourceGroup --location $location
```

## 3. Crear el workspace de Log Analytics

```powershell
$workspaceName = "law-sc200-repo-demo"

az monitor log-analytics workspace create `
  --resource-group $resourceGroup `
  --workspace-name $workspaceName `
  --location $location `
  --sku "PerGB2018"
```

Espera a que `provisioningState` muestre `Succeeded`.

## 4. Agregar Microsoft Sentinel

En Azure Portal:

1. Busca y abre **Microsoft Sentinel**.
2. Selecciona **Create**.
3. Selecciona el workspace `law-sc200-repo-demo` del grupo `rg-sc200`.
4. Selecciona **Add** y espera a que termine el onboarding.

## 5. Instalar la solución Azure Activity

En el workspace de Sentinel:

1. Abre **Content hub** (Centro de contenido).
2. Busca y selecciona **Azure Activity**.
3. Selecciona **Install** y espera a que termine.

## Resultado y siguiente paso

Al terminar, existe el grupo de recursos, el workspace de Log Analytics tiene Sentinel habilitado y la solución Azure Activity está instalada. Para empezar a recibir eventos, todavía falta configurar el conector de datos Azure Activity y asignar su ámbito a la suscripción que se desea supervisar.

## Comandos de esta preparación

```powershell
az login
az account set --subscription $subscriptionName
az account show --query "{Suscripcion:name,Estado:state,Tenant:tenantId}" -o table
az group create --name $resourceGroup --location $location
az monitor log-analytics workspace create --resource-group $resourceGroup --workspace-name $workspaceName --location $location --sku "PerGB2018"
```
