# Laboratorio 2 Detectar fallos 4625 en Windows con Sentinel

**SC-200 · Duración sugerida: 12–15 minutos**, incluida la espera de la regla. 

## Objetivo y requisitos

El SOC necesita detectar fallos repetidos contra un servidor sin revisar los registros a mano. Windows registra cada fallo como evento 4625. Sentinel recibe esos eventos, y una regla programada eleva a alerta los fallos que cumplen el umbral. Es como una recepción que anota cada acceso rechazado y avisa al supervisor cuando se repite.

**Tu objetivo.** generar tres fallos por comando, verlos con KQL en Defender y abrir la alerta dentro del incidente.

## 1 Verificá la ingesta antes de preparar la regla

Confirmá que WIN1 está encendida y que el workspace `law-sc200-hunting` recibe su tabla `SecurityEvent`. Necesitás Azure CLI autenticada en la suscripción del lab y acceso a Azure Run Command sobre WIN1.

Abrí [Microsoft Defender](https://security.microsoft.com/) → **Búsqueda avanzada**. Arriba a la derecha, seleccioná `law-sc200-hunting`. En una pestaña nueva ejecutá:

~~~kusto
SecurityEvent
| where TimeGenerated > ago(24h)
| summarize Eventos = count(), Fallos4625 = countif(EventID == 4625),
            UltimoEvento = max(TimeGenerated) by Computer
| order by UltimoEvento desc
~~~

**Comprobación.** Si WIN1 no aparece, revisá que esté encendida, que el conector Windows Security Events via AMA esté configurado y que la DCR asociada a la VM envíe al workspace seleccionado. Si aparece WIN1 con cero fallos, continuá con la prueba controlada.

## 2 Configurá la regla programada

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

1. En **General**, ingresá el nombre indicado arriba y verificá que la regla quede habilitada.
2. En **Establecer lógica de la regla**, pegá el KQL. Configurá **Ejecutar consulta cada 5 minutos** y **Buscar datos de los últimos 15 minutos**.
3. Elegí **Generar alerta cuando el número de resultados sea mayor que 0**. KQL devuelve una fila por equipo y usuario cuando hay al menos tres fallos. Por eso el umbral del asistente se aplica a las filas devueltas.
4. En **Configuración de incidentes**, habilitá la creación de incidentes a partir de las alertas. Revisá si la agrupación puede incorporar una alerta nueva a un incidente existente.
5. En **Revisar y crear**, confirmá los valores y guardá la regla antes de generar los fallos.

**Prueba de la lógica.** Antes de guardar, corré el mismo KQL en Búsqueda avanzada agregando `| where TimeGenerated > ago(24h)` inmediatamente después de `SecurityEvent`. Deberías ver una fila si hay tres fallos para el usuario de prueba. Para disparar la regla de 15 minutos, usá una tanda nueva de tres intentos seguidos.

## 3 Ubicá WIN1 desde PowerShell en tu PC

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

Confirmá que es tu VM del lab. Revisá su estado antes de ejecutar el script:

~~~powershell
az vm get-instance-view --subscription $subId `
  --resource-group $win1[0].resourceGroup --name $win1[0].name `
  --query "instanceView.statuses[?starts_with(code, 'PowerState/')].displayStatus" `
  -o tsv
~~~

Usá el siguiente bloque con la VM en ejecución. El archivo temporal evita problemas al pasar las comillas del script desde Windows PowerShell a Azure CLI. `LogonUser` intenta autenticar un usuario local ficticio con tipo 3 y registra la hora de cada intento para consultar solo los eventos nuevos.

## 4 Generá los fallos con Azure Run Command

Pegá el bloque completo en la misma consola:

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

Esperá tres rechazos con código Win32 `1326` y tres eventos 4625. A partir de aquí, seguí en el portal. Si Run Command devuelve un error, revisá el estado de la VM y el mensaje del agente antes de volver a lanzar el script. Si hubo tres rechazos y el conteo local es cero, comprobá la auditoría de fallos de inicio de sesión y la salida del comando dentro de la VM.

## 5 Verificá los tres eventos en Defender

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

Anotá la hora de los tres fallos y el usuario de prueba. Compará el resultado del portal con las marcas de tiempo de la salida de PowerShell, teniendo en cuenta la zona horaria.

## 6 Abrí el incidente y verificá la alerta

1. En Defender, abrí **Incidentes** y buscá el nombre de la regla.
2. Entrá al incidente y abrí **Alertas**. Si ya existía un incidente, revisá si recibió una alerta nueva.
3. Abrí la alerta. Compará su intervalo de actividad y los datos de la consulta, si están disponibles, con el equipo WIN1, el usuario ficticio y la hora de la tanda.
4. Si los 4625 ya están en Defender pero la alerta todavía no aparece, esperá la siguiente ejecución y verificá que la regla esté habilitada en el mismo workspace y que los tres eventos entren en su ventana de búsqueda. Si aparece la alerta pero no el incidente, revisá la configuración de incidentes y la agrupación.

**Entrega.** Guardá el conteo local, las tres filas de `SecurityEvent` y el identificador del incidente y de la alerta que coincide con tu tanda. Si solo existe un incidente anterior, comprobá si recibió la alerta nueva y marcá la vinculación como pendiente si aún no podés confirmarla.


## Referencias

- [Evento 4625 en Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625)
- [Reglas programadas de Microsoft Sentinel](https://learn.microsoft.com/azure/sentinel/detect-threats-custom)
- [Azure CLI Run Command](https://learn.microsoft.com/en-us/cli/azure/vm/run-command)
