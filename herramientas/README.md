# Herramientas: Microsoft Foundry DevPack (Windows)

Guía para preparar una PC nueva con PowerShell 7 para trabajar con Microsoft Foundry. Fuente oficial: https://aka.ms/foundrydevpack

> Este procedimiento instala herramientas locales. Crear recursos, desplegar modelos o ejecutar agentes en Azure son pasos posteriores que pueden generar costos.

## 1. Abrir PowerShell y comprobar lo que ya está instalado

Abre PowerShell 7 y ejecuta los comandos uno por uno. Si alguno indica que no existe, continúa con la instalación.

```powershell
$PSVersionTable.PSVersion
winget --version
git --version
az --version
azd version
code --version
py --version
```

Necesitas una suscripción de Azure activa y acceso al proyecto o recurso de Foundry que usarás. Si vas a trabajar con ejemplos Python, instala Python 3.10 o posterior. Git es necesario para clonar ejemplos. VS Code es opcional.

## 2. Instalar Foundry DevPack

```powershell
winget install Microsoft.FoundryDevPack
```

Acepta los términos del instalador si aparecen. Cuando termine, **cierra y vuelve a abrir PowerShell** para actualizar PATH. El DevPack instala las herramientas principales de Foundry, entre ellas Azure Developer CLI (`azd`) y su funcionalidad `azd ai`, y agrega la extensión de VS Code solo si VS Code ya está instalado. No instala VS Code ni GitHub Copilot App.

Si `winget` no está disponible, instala o actualiza **App Installer** de Microsoft y repite el paso. Consulta la página oficial antes de elegir otro método de instalación.

## 3. Verificar la instalación

En una ventana nueva de PowerShell:

```powershell
azd version
azd ai --help
```

Si aparece «comando no encontrado», reinicia PowerShell y, si usas VS Code, reinicia VS Code. Si ya tenías `azd` instalado, compara su versión y actualízalo cuando el instalador o `azd` lo indique.

## 4. Preparar Git y Python (solo si los usarás)

Para clonar repositorios, instala Git si `git --version` no funcionó. Para los ejemplos Python, instala Python 3.10 o posterior si `py --version` no funcionó. El DevPack no sustituye los paquetes Python específicos de cada demo.

En la carpeta del proyecto Python:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Instala las dependencias que indique el README de **ese** proyecto dentro del entorno virtual. No instales paquetes al azar para un demo que ya tiene `requirements.txt`.

## 5. Iniciar sesión en el tenant correcto antes de desplegar

Si tu demo requiere Azure, inicia sesión con la cuenta que tenga acceso al proyecto. Reemplaza `<TENANT_ID>` por el ID real de tu tenant; no copies literalmente los corchetes.

```powershell
az login --tenant <TENANT_ID> --use-device-code
az account show --output table
azd auth login --tenant-id <TENANT_ID> --use-device-code
```

Si `az` no existe, instala Azure CLI siguiendo la guía oficial: https://learn.microsoft.com/cli/azure/install-azure-cli-windows . Verifica también `az --version`.

Si tienes varias suscripciones, consulta primero cuáles ves y selecciona la correcta:

```powershell
az account list --output table
az account set --subscription "<NOMBRE_O_ID_DE_SUSCRIPCION>"
az account show --output table
```

**Antes de ejecutar `azd up`**, revisa el README y los parámetros del repo concreto, la región, el modelo, las cuotas disponibles y el costo estimado. No ejecutes un despliegue solo para comprobar que el DevPack quedó instalado.

## 6. En una PC nueva: traer esta guía

```powershell
New-Item -ItemType Directory -Path 'C:\clases' -Force | Out-Null
Set-Location 'C:\clases'
git clone https://github.com/frevar1975/training-templates.git
Set-Location 'C:\clases\training-templates\herramientas'
Get-Content .\README.md
```

Si ya clonaste el repositorio:

```powershell
Set-Location 'C:\clases\training-templates'
git pull origin main
Set-Location .\herramientas
```

## Problemas frecuentes

| Síntoma | Comprobación / acción |
| --- | --- |
| `azd` no se reconoce | Cierra y vuelve a abrir PowerShell; reinicia VS Code si usas su terminal. |
| `azd ai` no aparece | Comprueba `azd version` y repite o actualiza la instalación del DevPack según la guía oficial. |
| Inicio de sesión en tenant equivocado | Usa `--tenant` con `az login` y `--tenant-id` con `azd auth login`; confirma la cuenta y suscripción. |
| Python no aparece | Instala Python 3.10 o posterior; prueba `py --version` y abre una terminal nueva. |
| No hay permisos o cuota en Foundry | Revisa acceso al proyecto, roles, suscripción, región y cuota antes del despliegue. |

Documentación: https://learn.microsoft.com/azure/foundry/how-to/develop/install-cli-sdk
