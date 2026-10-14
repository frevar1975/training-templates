$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host 'Entorno seleccionado:'
azd env get-value AZURE_ENV_NAME
if ($LASTEXITCODE -ne 0) { throw 'Selecciona el entorno correcto con azd env select.' }
Write-Host 'Grupo que se eliminará:'
azd env get-value AZURE_RESOURCE_GROUP
if ($LASTEXITCODE -ne 0) { throw 'No se pudo obtener el grupo del entorno.' }
# azd conserva su confirmación interactiva de eliminación.
azd down
if ($LASTEXITCODE -ne 0) { throw 'La eliminación no terminó correctamente.' }
