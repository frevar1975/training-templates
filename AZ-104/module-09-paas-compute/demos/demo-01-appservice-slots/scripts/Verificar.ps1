$ErrorActionPreference = 'Stop'
$Prod = (azd env get-value PRODUCTION_URL).Trim()
if ($LASTEXITCODE -ne 0) { throw 'No se pudo obtener PRODUCTION_URL.' }
$Stage = (azd env get-value STAGING_URL).Trim()
if ($LASTEXITCODE -ne 0) { throw 'No se pudo obtener STAGING_URL.' }
foreach ($Endpoint in @(@{Nombre='Producción';Url=$Prod}, @{Nombre='Ensayo';Url=$Stage})) {
    $Info = Invoke-RestMethod "$($Endpoint.Url)/api/info"
    $Quote = Invoke-RestMethod "$($Endpoint.Url)/api/quote?product=audifonos&qty=2"
    [pscustomobject]@{Destino=$Endpoint.Nombre;Version=$Info.version;Subtotal=$Quote.subtotal;Descuento=$Quote.discount;Total=$Quote.total;Url=$Endpoint.Url}
}
