# Demo 2 · De tres fallos de inicio de sesión a un incidente en Sentinel

**SC-200 · Duración sugerida: 12–15 minutos**, incluida la espera de la regla. Presentar después del Demo 1, Azure Activity.

## Problema → solución → demo

El SOC necesita detectar fallos repetidos contra un servidor sin revisar los registros a mano. Windows registra cada fallo como evento 4625. Sentinel recibe esos eventos, y una regla programada eleva a alerta los fallos que cumplen el umbral. Es como una recepción que anota cada acceso rechazado y avisa al supervisor cuando se repite.

**Objetivo de clase:** generar tres fallos por comando, verlos con KQL en Defender y abrir la alerta dentro del incidente.

## 1. Prepará la regla antes de provocar los fallos

Confirmá que WIN1 está encendida y que el workspace `law-sc200-hunting` recibe su tabla `SecurityEvent`. Necesitás Azure CLI autenticada en la suscripción del lab y acceso a Azure Run Command sobre WIN1.

En **Microsoft Defender → Microsoft Sentinel → Análisis**, buscá **SC-200 | Tres fallos de inicio de sesión en WIN1**. Si ya existe, verificá que esté habilitada y revisá su configuración. Si falta, elegí **Crear → Regla de consulta programada** en ese workspace.

```kusto
SecurityEvent
| where EventID == 4625 and Computer =~ "WIN1"
| where TargetUserName =~ "sc200-demo-inexistente"
| summarize Intentos = count(), PrimerFallo = min(TimeGenerated),
            UltimoFallo = max(TimeGenerated)
            by Computer, TargetUserName
| where Intentos >= 3
```

Configurá ejecución cada **5 minutos**, búsqueda de los últimos **15 minutos**, alerta cuando la consulta devuelva **más de 0 filas** y creación de incidentes habilitada. El umbral de tres fallos está en KQL. Guardá la regla.

## 2. Provocá tres fallos desde PowerShell en tu PC

Confirmá primero la suscripción con `az account show -o table`. Ejecutá estos comandos en tu PC. Azure Run Command ejecuta el script dentro de WIN1 sin abrir RDP. Usá únicamente el usuario ficticio del lab.

```powershell
$subId = az account show --query id -o tsv
$vms = az vm list --subscription $subId -o json | ConvertFrom-Json
$win1 = @($vms | Where-Object {
    $_.name -ieq 'WIN1' -or $_.osProfile.computerName -ieq 'WIN1'
})
if ($win1.Count -ne 1) { throw 'Debe existir una sola VM WIN1 en la suscripcion.' }
$win1 | Select-Object name, resourceGroup
```

Confirmá que es tu VM del lab y pegá este bloque:

```powershell
$scriptFile = New-TemporaryFile
try {
    @'
$ErrorActionPreference = 'Stop'
if ($env:COMPUTERNAME -ine 'WIN1') { throw 'La VM debe ser WIN1.' }
$usuario = 'sc200-demo-inexistente'

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class SC200Logon {
    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool LogonUser(
        string user, string domain, string password,
        int logonType, int provider, out IntPtr token);
    [DllImport("kernel32.dll")]
    public static extern bool CloseHandle(IntPtr handle);
}
"@

$inicio = Get-Date
foreach ($intento in 1..3) {
    $token = [IntPtr]::Zero
    $ok = [SC200Logon]::LogonUser(
        $usuario, '.', 'SC200-Clave-Ficticia!', 3, 0, [ref]$token
    )
    $codigo = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
    if ($ok) {
        [void][SC200Logon]::CloseHandle($token)
        throw 'La cuenta se autentico. Prueba interrumpida.'
    }
    Write-Output "Intento $intento rechazado. Codigo Win32: $codigo"
    Start-Sleep -Seconds 2
}
$eventos = @(Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id = 4625
    StartTime = $inicio
} -ErrorAction SilentlyContinue | Where-Object {
    $_.Message -match [regex]::Escape($usuario)
})
Write-Output "Eventos 4625 encontrados en WIN1: $($eventos.Count)"
$eventos | Select-Object TimeCreated, Id, MachineName |
    Format-Table -AutoSize | Out-String
'@ | Set-Content -LiteralPath $scriptFile.FullName -Encoding Ascii

    az vm run-command invoke `
      --subscription $subId `
      --resource-group $win1[0].resourceGroup `
      --name $win1[0].name `
      --command-id RunPowerShellScript `
      --scripts "@$($scriptFile.FullName)" `
      --query 'value[].message' -o tsv
}
finally {
    Remove-Item -LiteralPath $scriptFile.FullName
}
```

Esperá tres rechazos con código Win32 `1326` y tres eventos 4625. A partir de aquí, seguí en el portal.

## 3. Investigá los eventos en Microsoft Defender

Abrí **Búsqueda avanzada**, seleccioná `law-sc200-hunting` y ejecutá:

```kusto
SecurityEvent
| where TimeGenerated > ago(30m)
| where EventID == 4625 and Computer =~ "WIN1"
| where TargetUserName =~ "sc200-demo-inexistente"
| project TimeGenerated, Computer, TargetUserName, LogonType, Status, SubStatus
| order by TimeGenerated asc
```

Mostrá el nombre de usuario, el equipo y la hora de los tres intentos. `LogonType = 3` corresponde a un inicio de sesión de red. `Status = 0xC000006D` indica un fallo de autenticación y `SubStatus = 0xC0000064` precisa que el usuario no existe. Si Windows ya devolvió los tres eventos y la consulta aún está vacía, repetí la búsqueda después de unos minutos.

## 4. Abrí el incidente y verificá la alerta

1. En Defender, abrí **Incidentes** y buscá el nombre de la regla.
2. Entrá al incidente y abrí **Alertas**. Si ya existía un incidente, revisá si recibió una alerta nueva.
3. Compará la actividad de la alerta con la hora de los tres 4625. Si aún falta, revisá la próxima ejecución de la regla y confirmá que la consulta devolvió una fila dentro de su ventana de 15 minutos.

**Resultado esperado:** aparecen tres 4625 nuevos y se puede identificar en Incidentes la alerta correspondiente a la tanda.

**Cierre para clase:** «El evento de Windows nos da el detalle de cada fallo. La regla detecta cuándo se repiten y el incidente reúne la alerta para que el analista pueda investigarla».

## Referencias

- [Evento 4625 en Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625)
- [Reglas programadas de Microsoft Sentinel](https://learn.microsoft.com/azure/sentinel/detect-threats-custom)
- [Azure CLI Run Command](https://learn.microsoft.com/en-us/cli/azure/vm/run-command)
