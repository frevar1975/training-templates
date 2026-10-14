param([Parameter(Mandatory=$true)][string]$Url,[int]$Clientes=12,[int]$Minutos=15)
$ErrorActionPreference='Stop'
if ($Clientes -lt 1 -or $Clientes -gt 32) { throw 'Usa entre 1 y 32 clientes.' }
if ($Minutos -lt 1 -or $Minutos -gt 30) { throw 'Usa entre 1 y 30 minutos.' }
$jobs=@()
try {
    1..$Clientes | ForEach-Object {
        $jobs += Start-Job -ArgumentList $Url.TrimEnd('/'),$Minutos -ScriptBlock {
            param($Base,$Duracion)
            $fin=(Get-Date).AddMinutes($Duracion)
            $ok=0;$fallos=0
            while ((Get-Date) -lt $fin) {
                try { $null=Invoke-WebRequest -Uri "$Base/work" -UseBasicParsing -TimeoutSec 30 -DisableKeepAlive; $ok++ }
                catch { $fallos++; Start-Sleep -Milliseconds 300 }
            }
            "Cliente terminado: $ok solicitudes correctas y $fallos fallidas"
        }
    }
    Write-Host "Carga iniciada: $Clientes clientes por $Minutos minutos. Ctrl+C para detener."
    while (@($jobs | Where-Object State -eq 'Running').Count -gt 0) {
        Write-Host "Carga activa $(Get-Date -Format HH:mm:ss)"
        Start-Sleep -Seconds 5
    }
    $jobs | Receive-Job
} finally {
    $jobs | Stop-Job -ErrorAction SilentlyContinue
    $jobs | Remove-Job -Force -ErrorAction SilentlyContinue
    Write-Host 'Clientes de este script detenidos.'
}
