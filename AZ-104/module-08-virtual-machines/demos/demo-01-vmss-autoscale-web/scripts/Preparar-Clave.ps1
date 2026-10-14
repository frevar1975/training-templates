$ErrorActionPreference='Stop'
$envName=azd env get-value AZURE_ENV_NAME
if ($LASTEXITCODE -ne 0 -or -not $envName) { throw 'Primero crea o selecciona el entorno azd de esta demo.' }
$existing=azd env get-values --output json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'No se pudo leer el entorno azd.' }
if ($existing.SSH_PUBLIC_KEY) { Write-Host 'El entorno ya tiene la clave pública del demo.'; exit 0 }
# Se genera solo la clave pública requerida por Linux. No se habilita SSH.
# La administración de esta demo se realiza con Azure Run Command.
$rsa=New-Object System.Security.Cryptography.RSACryptoServiceProvider -ArgumentList 2048
$wire=New-Object System.IO.MemoryStream
try {
    $rsa.PersistKeyInCsp=$false
    $public=$rsa.ExportParameters($false)
    function Write-Field([byte[]]$data) {
        $length=[uint32]$data.Length
        $wire.WriteByte([byte](($length -shr 24) -band 255))
        $wire.WriteByte([byte](($length -shr 16) -band 255))
        $wire.WriteByte([byte](($length -shr 8) -band 255))
        $wire.WriteByte([byte]($length -band 255))
        $wire.Write($data,0,$data.Length)
    }
    Write-Field ([System.Text.Encoding]::ASCII.GetBytes('ssh-rsa'))
    [byte[]]$exponent=$public.Exponent
    if ($exponent[0] -ge 128) { $exponent=[byte[]](@(0)+$exponent) }
    Write-Field $exponent
    [byte[]]$modulus=$public.Modulus
    if ($modulus[0] -ge 128) { $modulus=[byte[]](@(0)+$modulus) }
    Write-Field $modulus
    $key='ssh-rsa '+[Convert]::ToBase64String($wire.ToArray())+' az104-demo'
    azd env set SSH_PUBLIC_KEY $key
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo guardar la clave pública en azd.' }
    Write-Host 'Clave pública de laboratorio preparada. Se administrará con Run Command.'
} finally { $rsa.Dispose();$wire.Dispose() }
