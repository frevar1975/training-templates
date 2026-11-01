# MCT – Preparación de notebook Windows 11

Kit de reinstalación para laboratorios de AZ-104, AZ-305, AZ-400, SC-200, AI-900/AI-901/AI-3016, MCP y Power Platform.

## 1. Preparar Windows

- Actualizar Windows y controladores; revisar cámara, micrófono y sonido antes de la primera clase.
- Abrir PowerShell 7 como administrador. Si aún no está instalado, abrir Windows PowerShell y ejecutar:

```powershell
winget install --id Microsoft.PowerShell -e --source winget
```

- Para Docker Desktop, habilitar WSL 2 (en terminal como administrador):

```powershell
wsl --install
wsl --update
```

Si Windows solicita reiniciar, hacerlo antes de probar Docker. Revisar en BIOS que la virtualización esté habilitada.

## 2. Ejecutar instalador

Desde la carpeta con `setup-mct.ps1`:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\setup-mct.ps1
```

Opciones:

```powershell
# Agrega Wireshark/Nmap y clona repo público de plantillas
pwsh -NoProfile -ExecutionPolicy Bypass -File .\setup-mct.ps1 -IncludeSecurityTools -ClonePublicRepo

# Agrega además los módulos PowerShell Az y Microsoft.Graph
pwsh -NoProfile -ExecutionPolicy Bypass -File .\setup-mct.ps1 -InstallAzModules
```

El script es reutilizable: WinGet puede detectar programas ya instalados. Guarda registro en `~/MCT-Setup-Logs`. Algunos paquetes o extensiones pueden cambiar de identificador; si alguno falla, usa `winget search nombre` o `code --list-extensions`.

## 3. Configuración después de instalar

Cierra y abre PowerShell 7 para actualizar PATH:

```powershell
az login
az account list --output table
az bicep install
azd auth login
gh auth login

git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@example.com"
git config --global init.defaultBranch main
```

No se configuran automáticamente cuentas ni suscripciones para evitar errores de tenant.

## 4. Recuperar repositorios

```powershell
cd C:\clases
git clone https://github.com/frevar1975/training-templates.git
# Ejecutar solo si existe y tienes permisos:
gh repo clone frevar1975/training-delivery
```

Si se usó `-ClonePublicRepo`, no volver a clonar `training-templates`.

## 5. Pruebas de funcionamiento

```powershell
pwsh --version
az version
azd version
git --version
gh --version
python --version
node --version
docker --version
docker compose version
docker run --rm hello-world
wsl --status
```

La prueba `hello-world` requiere abrir Docker Desktop y esperar a que se inicie el motor.

## 6. Respaldo antes de formatear

```powershell
New-Item C:\Backup-MCT -ItemType Directory -Force
winget export --output C:\Backup-MCT\aplicaciones.json --accept-source-agreements
code --list-extensions | Set-Content C:\Backup-MCT\vscode-extensions.txt
git config --global --list | Set-Content C:\Backup-MCT\git-config.txt
```

La exportación **no** respalda documentos, claves SSH, secretos, tokens, repositorios con cambios locales, imágenes Docker ni recursos Azure. Copia tus archivos de `C:\clases`, claves y respaldos necesarios de forma segura por separado.

Para importar desde el equipo nuevo:

```powershell
winget import --import-file C:\Backup-MCT\aplicaciones.json --accept-package-agreements --accept-source-agreements
Get-Content C:\Backup-MCT\vscode-extensions.txt | ForEach-Object { code --install-extension $_ }
```

**Importante:** el instalador no crea máquinas virtuales ni recursos de pago en Azure y no altera automáticamente permisos de Defender.
