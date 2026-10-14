param(
    [ValidateRange(1,32)][int]$Clientes = 16,
    [ValidateRange(1,15)][int]$Minutos = 5
)
$ErrorActionPreference = 'Stop'
function EnvValue($Key) {
    $Value = azd env get-value $Key
    if ($LASTEXITCODE -ne 0 -or -not $Value) { throw "No existe $Key en azd." }
    return ($Value -join '').Trim()
}
$Url = EnvValue 'APPLICATION_URL'
$Uri = [uri]$Url
if ($Uri.Scheme -ne 'https' -or -not $Uri.Host.EndsWith('.azurecontainerapps.io')) {
    throw 'La URL debe ser la salida HTTPS de esta Container App.'
}
Write-Host "Carga del demo: $Clientes clientes por $Minutos minutos sobre $Url"
$Jobs = @()
try {
    1..$Clientes | ForEach-Object {
        $Jobs += Start-Job -ArgumentList $Url,$Minutos -ScriptBlock {
            param($Base,$Minutes)
            $End = (Get-Date).AddMinutes($Minutes)
            $Ok = 0; $Errors = 0; $Replicas = @{}
            while ((Get-Date) -lt $End) {
                try {
                    $R = Invoke-RestMethod -Uri "$Base/api/oferta" -TimeoutSec 90
                    $Ok++
                    if (-not $Replicas.ContainsKey($R.replica)) { $Replicas[$R.replica] = 0 }
                    $Replicas[$R.replica]++
                } catch { $Errors++; Start-Sleep -Seconds 1 }
                Start-Sleep -Milliseconds 100
            }
            [pscustomobject]@{Respuestas=$Ok;Errores=$Errors;Replicas=($Replicas | ConvertTo-Json -Compress)}
        }
    }
    while ($Jobs.State -contains 'Running') {
        $Finished = @($Jobs | Where-Object State -ne 'Running').Count
        Write-Host "Carga activa. Clientes finalizados: $Finished / $Clientes. Ctrl+C para detener."
        Start-Sleep -Seconds 15
    }
    $Jobs | Receive-Job | Format-Table -AutoSize
} finally {
    if ($Jobs) { $Jobs | Stop-Job; $Jobs | Remove-Job -Force }
}
