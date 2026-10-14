$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
function EnvValue($Key) {
    $Value = azd env get-value $Key
    if ($LASTEXITCODE -ne 0 -or -not $Value) { throw "Falta la variable $Key en azd." }
    return ($Value -join '').Trim()
}
$Subscription = EnvValue 'AZURE_SUBSCRIPTION_ID'
$Rg = EnvValue 'AZURE_RESOURCE_GROUP'
$App = EnvValue 'WEBAPP_NAME'
$Prod = EnvValue 'PRODUCTION_URL'
$Stage = EnvValue 'STAGING_URL'
$Packages = Join-Path $Root '.packages'
New-Item -ItemType Directory -Path $Packages -Force | Out-Null
foreach ($Release in @('v1', 'v2')) {
    $Zip = Join-Path $Packages "$Release.zip"
    Compress-Archive -Path (Join-Path $Root "apps/$Release/*") -DestinationPath $Zip -Force
    $AzArgs = @('webapp', 'deploy', '--subscription', $Subscription, '--resource-group', $Rg, '--name', $App, '--src-path', $Zip, '--type', 'zip', '--timeout', '600000')
    if ($Release -eq 'v2') { $AzArgs += @('--slot', 'staging') }
    & az @AzArgs
    if ($LASTEXITCODE -ne 0) { throw "Falló la publicación de $Release. Revisá el error y ejecutá nuevamente este script." }
}
function Wait-Version($Url, $Expected) {
    for ($Attempt = 1; $Attempt -le 30; $Attempt++) {
        try {
            $Info = Invoke-RestMethod "$Url/api/info" -TimeoutSec 15
            if ($Info.version -eq $Expected) { return }
        } catch { }
        Start-Sleep -Seconds 10
    }
    throw "No se confirmó la versión $Expected en $Url. Revisá Log stream en el portal."
}
Wait-Version $Prod '1.0'
Wait-Version $Stage '2.0'
Write-Host "Producción V1: $Prod"
Write-Host "Ensayo V2: $Stage"
Write-Host 'Ambas versiones verificadas. No vuelvas a aprovisionar durante el ensayo: este hook restaura V1/V2.'
