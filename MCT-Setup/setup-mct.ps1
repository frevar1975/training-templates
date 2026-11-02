#requires -Version 7.0
<#
.SYNOPSIS
  Prepara una notebook Windows 11 para dictar cursos Microsoft (MCT).
.DESCRIPTION
  Instala herramientas con WinGet, extensiones VS Code, y crea C:\clases.
  Configura módulos locales en C:\PowerShell\Modules sin depender de OneDrive.
  No inicia sesión, no despliega recursos Azure ni clona repositorios privados automáticamente.
.EXAMPLE
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\setup-mct.ps1
.EXAMPLE
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\setup-mct.ps1 -IncludeSecurityTools -ClonePublicRepo
#>
[CmdletBinding()]
param(
    [switch]$IncludeSecurityTools,
    [switch]$ClonePublicRepo,
    [switch]$InstallAzModules,
    [string]$ModulesPath = 'C:\PowerShell\Modules',
    [string]$ClassesPath = 'C:\clases'
)

$ErrorActionPreference = 'Stop'
$logDir = Join-Path $env:USERPROFILE 'MCT-Setup-Logs'
New-Item -Path $logDir -ItemType Directory -Force | Out-Null
$logPath = Join-Path $logDir ('setup-mct-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
Start-Transcript -Path $logPath | Out-Null

try {
    Write-Host '=== Instalador de herramientas MCT ===' -ForegroundColor Cyan
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'WinGet no está disponible. Actualiza App Installer desde Microsoft Store y vuelve a ejecutar.'
    }

    $packages = @(
        'Microsoft.PowerShell',
        'Microsoft.WindowsTerminal',
        'Microsoft.AzureCLI',
        'Microsoft.Azd',
        'Git.Git',
        'GitHub.cli',
        'Microsoft.VisualStudioCode',
        'Docker.DockerDesktop',
        'Python.Python.3.13',
        'OpenJS.NodeJS.LTS',
        'Microsoft.Azure.StorageExplorer',
        'Postman.Postman',
        'OBSProject.OBSStudio',
        '7zip.7zip'
    )
    if ($IncludeSecurityTools) {
        $packages += 'WiresharkFoundation.Wireshark', 'Insecure.Nmap'
    }

    $failed = [System.Collections.Generic.List[string]]::new()
    foreach ($package in $packages) {
        Write-Host "`n==> $package" -ForegroundColor Cyan
        try {
            & winget install --id $package --exact --source winget --accept-package-agreements --accept-source-agreements --disable-interactivity
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "WinGet devolvió código $LASTEXITCODE para $package."
                $failed.Add($package)
            }
        }
        catch {
            Write-Warning "No se pudo instalar $package : $($_.Exception.Message)"
            $failed.Add($package)
        }
    }

    $folders = @('AZ-104','AZ-305','AZ-400','SC-200','AI-900','AI-901','AI-3016','AB-730','PL-900','MCP','Docker','Demos')
    foreach ($folder in $folders) {
        New-Item -Path (Join-Path $ClassesPath $folder) -ItemType Directory -Force | Out-Null
    }
    Write-Host "`nCarpetas creadas: $ClassesPath" -ForegroundColor Green

    # Si VS Code fue instalado en esta misma ejecución, puede que todavía no esté en PATH.
    $code = Get-Command code -ErrorAction SilentlyContinue
    if (-not $code) {
        $candidates = @(
            (Join-Path $env:LOCALAPPDATA 'Programs\Microsoft VS Code\bin\code.cmd'),
            (Join-Path $env:ProgramFiles 'Microsoft VS Code\bin\code.cmd')
        )
        $codePath = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    }
    else { $codePath = $code.Source }

    $extensions = @(
        'ms-vscode.powershell',
        'ms-python.python',
        'ms-azuretools.vscode-bicep',
        'ms-azuretools.vscode-docker',
        'ms-azuretools.vscode-azurefunctions',
        'ms-toolsai.jupyter',
        'ms-vscode.azurecli'
    )
    if ($codePath) {
        foreach ($extension in $extensions) {
            Write-Host "Extension VS Code: $extension"
            & $codePath --install-extension $extension --force
            if ($LASTEXITCODE -ne 0) { Write-Warning "Revisar extensión $extension" }
        }
    }
    else {
        Write-Warning 'No se encontró code en PATH. Abre una terminal nueva y ejecuta los comandos de extensiones del README.'
    }

    # MCT: priorizar módulos locales y evitar rutas OneDrive (sin borrar archivos).
    New-Item -Path $ModulesPath -ItemType Directory -Force | Out-Null
    $configuredModulePath = @(
        $ModulesPath
        @($env:PSModulePath -split ';' | Where-Object {
            $_ -and $_ -ne $ModulesPath -and $_ -notlike '*OneDrive*'
        })
    ) | Select-Object -Unique
    $env:PSModulePath = $configuredModulePath -join ';'

    # Registrar ruta de usuario; PowerShell puede agregar rutas predeterminadas al iniciar.
    [Environment]::SetEnvironmentVariable('PSModulePath', $ModulesPath, 'User')

    # Bloque delimitado e idempotente en el perfil PowerShell 7 para corregir rutas al inicio.
    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileFolder = Split-Path -Parent $profilePath
    New-Item -Path $profileFolder -ItemType Directory -Force | Out-Null
    $profileText = if (Test-Path -LiteralPath $profilePath) {
        Get-Content -LiteralPath $profilePath -Raw
    } else { '' }
    $startMarker = '# >>> MCT LOCAL MODULES >>>'
    $endMarker = '# <<< MCT LOCAL MODULES <<<'
    # Generar el bloque sin interpolar variables de PowerShell en tiempo de instalación.
    $profileBlock = @'
# >>> MCT LOCAL MODULES >>>
$mctModuleRoot = '__MCT_MODULE_PATH__'
$mctModulePaths = @(
    $mctModuleRoot
    @($env:PSModulePath -split ';' | Where-Object {
        $_ -and $_ -ne $mctModuleRoot -and $_ -notlike '*OneDrive*'
    })
) | Select-Object -Unique
$env:PSModulePath = $mctModulePaths -join ';'
# <<< MCT LOCAL MODULES <<<
'@.Replace('__MCT_MODULE_PATH__', $ModulesPath.Replace("'", "''"))

    if ($profileText.Contains($startMarker) -and $profileText.Contains($endMarker)) {
        $pattern = '(?s)' + [regex]::Escape($startMarker) + '.*?' + [regex]::Escape($endMarker)
        $profileText = [regex]::Replace($profileText, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $profileBlock })
    }
    elseif ($profileText -match '# MCT - MODULOS POWERSHELL LOCALES') {
        # Actualizar bloque legado creado manualmente durante la migración.
        $pattern = '(?s)# =+\r?\n# MCT - MODULOS POWERSHELL LOCALES\r?\n# =+.*?\$env:PSModulePath\s*=\s*\$rutas\s*-join\s*["'']?;["'']?'
        $profileText = [regex]::Replace($profileText, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $profileBlock })
        if (-not $profileText.Contains($startMarker)) { $profileText += "`r`n" + $profileBlock }
    }
    else { $profileText += "`r`n" + $profileBlock }
    Set-Content -LiteralPath $profilePath -Value $profileText -Encoding utf8
    Write-Host "Módulos locales: $ModulesPath; perfil: $profilePath" -ForegroundColor Green

    if ($InstallAzModules) {
        Write-Host "Verificando módulos en $ModulesPath..." -ForegroundColor Cyan
        foreach ($module in @('Az', 'Microsoft.Graph')) {
            $localModule = Get-Module -ListAvailable -Name $module |
                Where-Object { $_.Path.StartsWith($ModulesPath + '\', [System.StringComparison]::OrdinalIgnoreCase) } |
                Sort-Object Version -Descending | Select-Object -First 1
            if ($localModule) {
                Write-Host "$module ya disponible en C: ($($localModule.Version)); se omite descarga." -ForegroundColor Green
                continue
            }
            try {
                Save-Module -Name $module -Path $ModulesPath -Repository PSGallery -ErrorAction Stop
                Write-Host "$module descargado en $ModulesPath" -ForegroundColor Green
            }
            catch {
                Write-Warning "No se pudo guardar módulo $module : $($_.Exception.Message)"
                $failed.Add("PowerShell:$module")
            }
        }
        foreach ($module in @('Az.Accounts','Microsoft.Graph.Authentication')) {
            try {
                Import-Module $module -ErrorAction Stop
                $loaded = Get-Module -Name $module
                if (-not $loaded.Path.StartsWith($ModulesPath + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
                    Write-Warning "$module se cargó fuera de $ModulesPath : $($loaded.Path)"
                } else { Write-Host "$module OK: $($loaded.Path)" -ForegroundColor Green }
            }
            catch {
                Write-Warning "Falló la validación de $module : $($_.Exception.Message)"
                $failed.Add("Import:$module")
            }
        }
    }

    if ($ClonePublicRepo) {
        $gitCommand = Get-Command git -ErrorAction SilentlyContinue
        if (-not $gitCommand) {
            $gitFallback = Join-Path $env:ProgramFiles 'Git\cmd\git.exe'
            if (Test-Path $gitFallback) { $gitCommand = @{ Source = $gitFallback } }
        }
        $repoPath = Join-Path $ClassesPath 'training-templates'
        if (Test-Path $repoPath) {
            Write-Host 'El repositorio training-templates ya existe: se omite el clone.'
        }
        elseif ($gitCommand) {
            & $gitCommand.Source clone 'https://github.com/frevar1975/training-templates.git' $repoPath
        }
        else { Write-Warning 'Git no está disponible aún. Clona el repositorio tras reiniciar la terminal.' }
    }

    Write-Host "`n=== Resultado ===" -ForegroundColor Cyan
    if ($failed.Count) {
        Write-Warning ('Revisar paquetes: ' + ($failed -join ', '))
    }
    else { Write-Host 'WinGet finalizó sin errores reportados.' -ForegroundColor Green }
    Write-Host "Log: $logPath"
    Write-Host 'IMPORTANTE: Docker Desktop necesita WSL 2 y virtualización habilitada. Ejecuta wsl --install y reinicia si corresponde.'
    Write-Host 'Vuelve a abrir PowerShell para renovar PATH. Revisa README.md para autenticar Azure, GitHub y azd.'
}
finally {
    Stop-Transcript | Out-Null
}
