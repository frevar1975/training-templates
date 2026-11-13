# Demo de eventos de seguridad de Windows en Microsoft Sentinel

Guía base para crear una VM Windows, instalar Azure Monitor Agent (AMA), asociar una DCR para el evento 4625 y comprobar la ingesta en Microsoft Sentinel. Esta plantilla llega hasta la consulta del evento; la creación de una regla analítica de alerta queda fuera del alcance.

**Terminal:** Windows PowerShell 5.1 con Azure CLI.  
**Región de ejemplo:** `eastus`.  
**Privacidad:** no subas IDs de suscripción, contraseñas, claves, IP públicas ni datos personales.

## Valores que debes revisar

| Parámetro | Ejemplo de esta ejecución |
|---|---|
| Grupo de recursos de VM y DCR | `rg-sc200-windows-demo` |
| VM | `winsentdemo` |
| Workspace | `law-sc200-repo-demo` |
| Grupo del workspace | `rg-sc200` |
| DCR | `dcr-windows-4625-demo` |
| Asociación | `assoc-win-4625-demo` |
| Filtro | `Security!*[System[(EventID=4625)]]` |

Sustituye los nombres por recursos de tu propio laboratorio y confirma que el workspace seleccionado en Sentinel sea el destino configurado en la DCR.

## 1. Crear recursos de laboratorio

Crea un grupo dedicado:

```powershell
az group create --name "rg-sc200-windows-demo" --location "eastus" -o table
```

Solicita la contraseña sin incluirla en el historial:

```powershell
$securePassword = Read-Host "Contraseña para azureuser" -AsSecureString
$adminPassword = [System.Net.NetworkCredential]::new("", $securePassword).Password

az vm create `
  --resource-group "rg-sc200-windows-demo" `
  --name "winsentdemo" `
  --location "eastus" `
  --image "Win2022Datacenter" `
  --size "Standard_B2s" `
  --admin-username "azureuser" `
  --admin-password $adminPassword `
  --nsg-rule "NONE"

Remove-Variable adminPassword, securePassword
```

Mantén corto el nombre de VM para evitar que el nombre del equipo Windows supere los 15 caracteres. `--nsg-rule NONE` no abre RDP entrante; administra la VM con Run Command. Verifica que la imagen elegida siga disponible y soportada.

## 2. Instalar AMA

```powershell
az vm identity assign `
  --resource-group "rg-sc200-windows-demo" `
  --name "winsentdemo"

az vm extension set `
  --resource-group "rg-sc200-windows-demo" `
  --vm-name "winsentdemo" `
  --name "AzureMonitorWindowsAgent" `
  --publisher "Microsoft.Azure.Monitor" `
  --enable-auto-upgrade true
```

Confirma `AzureMonitorWindowsAgent` en estado `Succeeded`:

```powershell
az vm extension list `
  --resource-group "rg-sc200-windows-demo" `
  --vm-name "winsentdemo" `
  --query "[].{Nombre:name,Estado:provisioningState}" -o table
```

## 3. Crear una DCR de Windows Security Events via AMA

Obtén el ID del workspace:

```powershell
$workspaceResourceId = az monitor log-analytics workspace show `
  --resource-group "rg-sc200" `
  --workspace-name "law-sc200-repo-demo" `
  --query id -o tsv
```

Crea el payload de la regla. Cambia los nombres de recurso o el XPath si tu demo usa otros valores:

```powershell
$subscriptionId = az account show --query id -o tsv
$dcrResourceId = "/subscriptions/$subscriptionId/resourceGroups/rg-sc200-windows-demo/providers/Microsoft.Insights/dataCollectionRules/dcr-windows-4625-demo"

$dcr = @{
  location = "eastus"
  kind = "Windows"
  properties = @{
    dataSources = @{
      windowsEventLogs = @(
        @{
          streams = @("Microsoft-SecurityEvent")
          xPathQueries = @("Security!*[System[(EventID=4625)]]")
          name = "windowsSecurity4625"
        }
      )
    }
    destinations = @{
      logAnalytics = @(
        @{
          workspaceResourceId = $workspaceResourceId
          name = "sentinelWorkspace"
        }
      )
    }
    dataFlows = @(
      @{
        streams = @("Microsoft-SecurityEvent")
        destinations = @("sentinelWorkspace")
      }
    )
  }
}

$dcrPath = Join-Path $PWD "dcr-windows-4625.json"
$dcrJson = $dcr | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($dcrPath, $dcrJson, [System.Text.UTF8Encoding]::new($false))

az rest `
  --method put `
  --url "https://management.azure.com$dcrResourceId`?api-version=2023-03-11" `
  --body "@$dcrPath"
```

La respuesta debe confirmar una DCR `Windows` en `eastus` con estado de aprovisionamiento `Succeeded`. El destino debe ser el workspace donde Sentinel está habilitado.

## 4. Asociar la regla a la VM

```powershell
$vmId = az vm show `
  --resource-group "rg-sc200-windows-demo" `
  --name "winsentdemo" `
  --query id -o tsv

az monitor data-collection rule association create `
  --name "assoc-win-4625-demo" `
  --resource $vmId `
  --rule-id $dcrResourceId
```

La asociación le indica a Azure que aplique la DCR a esa VM.

## 5. Generar un evento 4625 de prueba

Verifica primero la auditoría de inicio de sesión:

```powershell
az vm run-command invoke `
  --resource-group "rg-sc200-windows-demo" `
  --name "winsentdemo" `
  --command-id "RunPowerShellScript" `
  --scripts 'auditpol /get /subcategory:"Logon"' `
  --query "value[0].message" -o tsv
```

Debe auditar fallos. Si no lo hace, habilítalos en la VM:

```powershell
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
```

Provoca un intento de autenticación de red contra localhost con una cuenta inexistente y contraseña ficticia:

```powershell
az vm run-command invoke `
  --resource-group "rg-sc200-windows-demo" `
  --name "winsentdemo" `
  --command-id "RunPowerShellScript" `
  --scripts "net.exe use \\localhost\IPC$ /user:winsentdemo\sc200demo-falso2 Clave-Falsa-Para-Demo-2026!; Start-Sleep -Seconds 2; `$e = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625; StartTime=(Get-Date).AddMinutes(-2)} -MaxEvents 1 -ErrorAction SilentlyContinue; if (`$e) { Write-Output ('EVENTO_LOCAL_OK: ' + `$e.TimeCreated + ' | ' + `$e.Id) } else { Write-Output 'EVENTO_LOCAL_NO_ENCONTRADO' }" `
  -o json
```

El error 1326 es esperado: las credenciales de prueba son falsas. Esta acción es local a la VM, no simula un atacante externo ni un acceso exitoso.

## 6. Consultar en Sentinel

En Advanced hunting o Logs, selecciona el workspace correcto.

Comprueba que AMA envíe Heartbeat:

```kusto
Heartbeat
| where Category == "Azure Monitor Agent"
| where Computer contains "winsentdemo"
| where TimeGenerated > ago(1h)
| take 10
```

Consulta el evento de seguridad:

```kusto
SecurityEvent
| where TimeGenerated > ago(2h)
| where EventID == 4625
| where Computer contains "winsentdemo"
| project TimeGenerated, Computer, EventID, Account, IpAddress, Activity
| order by TimeGenerated desc
```

El criterio de éxito es una fila reciente en `SecurityEvent` para la VM con `EventID` 4625 y el detalle de inicio de sesión fallido. En la ejecución base, la consulta devolvió una fila para `winsentdemo`.

## Alcance y limpieza

Esta plantilla demuestra la ingesta y consulta de un evento. No crea una regla analítica, una alerta ni un incidente. Para demostrar alertas, crea una regla analítica aparte.

Cuando termine el laboratorio, elimina solo el grupo dedicado de la VM/DCR después de confirmar que no contiene recursos que quieras conservar:

```powershell
az group delete --name "rg-sc200-windows-demo" --yes --no-wait
```

El workspace del ejemplo está en `rg-sc200`; no lo elimines al limpiar la VM.
