$ErrorActionPreference = 'Stop'
function EnvValue($Key) {
    $Value = azd env get-value $Key
    if ($LASTEXITCODE -ne 0 -or -not $Value) { throw "No existe $Key en azd." }
    return ($Value -join '').Trim()
}
$Url = EnvValue 'APPLICATION_URL'
Write-Output $Url
Start-Process $Url
