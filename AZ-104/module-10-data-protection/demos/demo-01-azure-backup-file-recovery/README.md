# Demo 01 · Recuperar un archivo con Azure Backup

## Objetivo

Demostrar que Azure Backup permite recuperar un archivo eliminado desde un punto de recuperación de una VM Windows, sin restaurar la VM completa.

## Prerrequisitos

- Una VM Windows de laboratorio protegida por Azure Backup en un Recovery Services vault.
- Un trabajo de backup completado cuyo punto de recuperación sea posterior a la creación del archivo.
- Acceso al portal para abrir **File Recovery** y descargar el ejecutable de recuperación.
- El equipo local debe tener conectividad y permisos de administrador para ejecutar el proceso de recuperación.

> Para una repetición totalmente desde cero, crea primero la VM, el vault y la política de backup. No continúes hasta que el primer backup haya finalizado correctamente.

## Ejecución

### 1. Crear archivo de prueba dentro de la VM

Ejecuta en una sesión de PowerShell dentro de la VM, no en el equipo local:

```powershell
New-Item -Path "C:\DemoBackup" -ItemType Directory -Force
"Archivo de prueba para Azure Backup. Creado el $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')." |
  Set-Content -Path "C:\DemoBackup\reporte-cierre.txt"
Get-Content "C:\DemoBackup\reporte-cierre.txt"
```

Conserva el contenido/fecha para poder comparar después.

### 2. Crear un punto de recuperación que contenga el archivo

En Azure Portal, abre la VM protegida y su configuración de **Backup**. Ejecuta **Backup now** si hace falta. Espera a que el trabajo finalice con estado **Completed** y confirma que el punto de recuperación sea posterior a la creación del archivo.

No borres el archivo antes de que exista ese punto de recuperación.

### 3. Simular el borrado

En la PowerShell de la VM:

```powershell
Test-Path "C:\DemoBackup\reporte-cierre.txt"
Remove-Item "C:\DemoBackup\reporte-cierre.txt"
Test-Path "C:\DemoBackup\reporte-cierre.txt"
```

El resultado final esperado de Test-Path es `False`.

### 4. Recuperar el archivo desde el PC

En el portal, abre el vault y el elemento protegido de la VM. Selecciona **File Recovery**, elige el punto de recuperación que contiene el archivo y descarga el ejecutable.

Ejecuta el archivo descargado **como administrador en el PC desde el cual navegarás y copiarás el archivo**. Cuando el ejecutable pida una contraseña, usa exactamente la contraseña temporal que muestra el portal en esa sesión de File Recovery; no es la contraseña de Windows ni la de Azure.

Espera a que conecte el destino iSCSI y monte los volúmenes. La unidad puede recibir una letra diferente; no supongas que siempre será E:.

Busca:

```text
<unidad_recuperada>:\DemoBackup\reporte-cierre.txt
```

Copia el archivo a una carpeta normal del PC y valida su contenido:

```powershell
New-Item -Path "$env:USERPROFILE\Desktop\Recuperado" -ItemType Directory -Force
Copy-Item -Path "E:\DemoBackup\reporte-cierre.txt" -Destination "$env:USERPROFILE\Desktop\Recuperado\reporte-cierre.txt"
Get-Content "$env:USERPROFILE\Desktop\Recuperado\reporte-cierre.txt"
```

Sustituye E: por la letra que realmente se montó.

### 5. Cerrar la recuperación

En el portal, pulsa **Unmount Disks** en File Recovery y espera a que termine. Después pulsa Q en la ventana del ejecutable para cerrarlo. Comprueba que la copia local sigue disponible.

## Evidencia para clase

- Archivo creado y leído dentro de la VM.
- Backup completado y punto de recuperación disponible.
- `Test-Path` devuelve False después del borrado.
- Archivo visible en el volumen recuperado y copiado al PC.
- Contenido recuperado coincide con el archivo original.
- Portal confirma **Unmount Disks**.

## Preguntas para el grupo

- ¿Por qué el punto de recuperación debe ser posterior a la creación del archivo?
- ¿Qué diferencia hay entre recuperar un archivo y restaurar la VM completa?
- ¿Por qué se deben desmontar los discos al terminar?
