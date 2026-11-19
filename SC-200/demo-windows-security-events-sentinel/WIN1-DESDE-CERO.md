# SC-200 desde cero con WIN1 y Microsoft Sentinel

Prepará el ambiente y validá un fallo de inicio de sesión desde Windows hasta Sentinel, con RDP cerrado. Usá una suscripción de laboratorio con permisos sobre la VM, el workspace y las reglas de recopilación. Los nombres, la región y el tamaño son valores de ejemplo.

## 1. Crear el ambiente en PowerShell

Iniciá sesión con `az login` si hace falta y confirmá la suscripción activa antes de crear recursos.

```powershell
az account show -o table
$rg = 'rg-sc200-hunting'
$loc = 'eastus2'
$law = 'law-sc200-hunting'
$vm = 'WIN1'
$image = 'MicrosoftWindowsServer:WindowsServer:2022-datacenter-g2:latest'
az group create -n $rg -l $loc -o none
az vm create -g $rg -n $vm -l $loc --image $image --size Standard_D2s_v5 --admin-username sc200admin --public-ip-sku Standard --nsg-rule NONE --no-wait
```

Azure CLI solicita la contraseña del administrador. Verificá imagen, tamaño y cuota antes de clase. La imagen usada emitió un aviso de deprecación con bloqueo anunciado para el 1 de febrero de 2027. Para futuros despliegues, elegí una imagen de Windows Server compatible si Azure deja de admitirla.

Mientras se aprovisiona WIN1, creá el workspace y habilitá Sentinel.

```powershell
az provider register -n Microsoft.SecurityInsights --wait
$lawId = az monitor log-analytics workspace create -g $rg -n $law -l $loc --query id -o tsv
$sentinelUrl = "$lawId/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=2025-09-01"
$bodyFile = Join-Path $env:TEMP 'sc200-sentinel-onboarding.json'
Set-Content -Path $bodyFile -Value '{"properties":{"customerManagedKey":false}}' -Encoding ascii
az rest --method put --url $sentinelUrl --headers "Content-Type=application/json" --body "@$bodyFile" --query "{Estado:name, Tipo:type}" -o table
az vm show -g $rg -n $vm -d --query powerState -o tsv
```

Esperá `default` y `Microsoft.SecurityInsights/onboardingStates` en la respuesta de Sentinel y `VM running` para la VM. El archivo JSON y el encabezado explícito resuelven el HTTP 415 observado al pasar el JSON en línea desde PowerShell.

## 2. Instalar el conector y asociar WIN1

1. Abrí [Microsoft Defender](https://security.microsoft.com) y seleccioná `law-sc200-hunting`. Si no aparece, verificá el tenant y la conexión del workspace a Defender.
2. En **Microsoft Sentinel → Administración de contenido → Concentrador de contenido**, instalá **Windows Security Events**.
3. En **Configuración → Conectores de datos**, buscá **Windows Security Events via AMA** y abrí la página del conector. Si solo se ve Microsoft 365, quitá los filtros **SecurityAlert (OfficeIRM)** y **Connected**, y actualizá.
4. Creá la DCR `dcr-win1-security`. Agregá `WIN1` como recurso y verificá que el destino sea `law-sc200-hunting`. Elegí **Común / Common** para incluir 4625 y 4624.
5. Guardá y esperá el aprovisionamiento de `AzureMonitorWindowsAgent`. En **Búsqueda avanzada** de Defender, ejecutá la siguiente consulta en el workspace del lab.

```kusto
Heartbeat
| where TimeGenerated > ago(1h)
| where Computer =~ "WIN1" or Computer startswith "WIN1."
| summarize UltimoLatido = max(TimeGenerated) by Computer
```

## 3. Generar y comprobar el 4625 en Windows

Ejecutá desde PowerShell local. Azure Run Command hace una sola solicitud de autenticación local en WIN1 con una cuenta ficticia que debe permanecer inexistente.

```powershell
$scriptFile = Join-Path $env:TEMP 'sc200-probar-4625.ps1'
@'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class DemoLogon {
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool LogonUser(string user, string domain,
        string password, int logonType, int provider, out IntPtr token);
}
"@
$token = [IntPtr]::Zero
$usuario = 'sc200-demo-inexistente'
$resultado = [DemoLogon]::LogonUser($usuario, $env:COMPUTERNAME,
    'ClaveFicticia-4625!', 3, 0, [ref]$token)
"Autenticacion exitosa: $resultado"
'@ | Set-Content -Path $scriptFile -Encoding ascii
az vm run-command invoke -g $rg -n $vm --command-id RunPowerShellScript --scripts "@$scriptFile" --query "value[].message" -o tsv
```

La salida esperada es `Autenticacion exitosa: False`. Comprobá la auditoría y el registro local con una segunda ejecución. El archivo conserva las comillas que se perdieron en la prueba con el diagnóstico en línea.

```powershell
$diagFile = Join-Path $env:TEMP 'sc200-diagnostico-4625.ps1'
@'
auditpol.exe /get '/subcategory:{0CCE9215-69AE-11D9-BED3-505054503030}'
$eventos = Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id = 4625
    StartTime = (Get-Date).AddHours(-1)
} -ErrorAction SilentlyContinue
$prueba = $eventos | Where-Object {
    $_.ToXml() -match 'sc200-demo-inexistente'
} | Select-Object -First 1
if ($prueba) {
    $prueba | Format-List TimeCreated, Id, MachineName, Message
} else {
    'No se encontro el 4625 de la cuenta de prueba en la ultima hora.'
}
'@ | Set-Content -Path $diagFile -Encoding ascii
az vm run-command invoke -g $rg -n $vm --command-id RunPowerShellScript --scripts "@$diagFile" --query "value[].message" -o tsv
```

Verificá que **Logon** audite fallos y que exista un **4625** para la cuenta ficticia. El subestado `0xC0000064` corresponde a un usuario inexistente. El tipo `3` es el tipo de inicio solicitado por el script desde WIN1.

## 4. Confirmar la ingesta en Sentinel

En **Búsqueda avanzada**, elegí `law-sc200-hunting` y ejecutá este bloque en una consulta nueva. Si usás otro nombre de VM, ajustá el filtro de equipo.

```kusto
SecurityEvent
| where TimeGenerated > ago(2h)
| where Computer =~ "WIN1" or Computer startswith "WIN1."
| where EventID == 4625
| where TargetUserName =~ "sc200-demo-inexistente"
| project TimeGenerated, Computer, EventID, TargetUserName, LogonType
| order by TimeGenerated desc
```

- Si aparece `descSecurityEvent`, reemplazá el editor por un único bloque de KQL.
- Si Defender muestra un error inesperado, probá `SecurityEvent | take 10` en una pestaña nueva o desde **Azure → Log Analytics → workspace → Registros**.
- Si hay `Heartbeat` pero falta el 4625, revisá la asociación de WIN1, el filtro de eventos y el destino de la DCR. Si la primera prueba precedió al aprovisionamiento del agente, generá un evento nuevo y consultá unos minutos después.
- Compará equipo, cuenta, ID y hora. La VM y Defender pueden mostrar zonas horarias distintas.

El demo termina cuando aparece el mismo 4625 en Windows y en `SecurityEvent`. Para iniciar el Demo 3, preguntá al grupo si el fallo fue aislado y ampliá la búsqueda por cuenta y ventana de tiempo.

## Referencias

- [Habilitar Sentinel](https://learn.microsoft.com/azure/sentinel/quickstart-onboard)
- [Conectores de Windows en Sentinel](https://learn.microsoft.com/azure/sentinel/connect-services-windows-based)
- [Azure Run Command en Windows](https://learn.microsoft.com/azure/virtual-machines/windows/run-scripts-in-vm)
- [Evento de Windows 4625](https://learn.microsoft.com/windows/security/threat-protection/auditing/event-4625)
