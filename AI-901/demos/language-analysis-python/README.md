# Laboratorio web de análisis de texto con Azure AI Language

Aplicación educativa en Python y Flask. Permite elegir una operación, escribir texto en una página web y enviar el análisis al recurso de Azure AI Language.

## Tareas disponibles

- Detección de idioma.
- Detección de información personal (PII).
- Extracción de frases clave.
- Reconocimiento de entidades.
- Análisis de sentimiento.
- Resumen introductorio mediante frases clave.

> **Nota sobre el resumen:** la opción introductoria presenta frases clave como ideas principales. No llama a un servicio dedicado de resumen generativo. Para el laboratorio de Microsoft, el resumen se realiza con un modelo generativo en Chat Playground.

## Descargar y ubicar el proyecto

Si todavía no tienes una copia local del repositorio, clónalo:

```powershell
git clone https://github.com/frevar1975/training-templates.git
```

Entra en la carpeta de este demo:

```powershell
Set-Location AI-901/demos/language-analysis-python
```

Si ya tienes el repositorio, abre PowerShell en su carpeta y ejecuta el comando `Set-Location` anterior.

## Requisitos

- Windows 10/11.
- Python 3.10 o superior.
- Un recurso de Azure AI Language con endpoint y clave.

## Ejecutar en Windows PowerShell

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
py -m venv .venv
```

Activa el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, ejecuta este comando solo para la sesión actual y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Crea tu archivo local de configuración:

```powershell
Copy-Item .env.example .env
notepad .env
```

En `.env`, reemplaza los valores de ejemplo con el endpoint y la clave de tu recurso:

```text
LANGUAGE_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
LANGUAGE_KEY=tu-clave
```

Guarda el archivo y ejecuta la aplicación:

```powershell
python web_app.py
```

Abre en tu navegador: <http://127.0.0.1:5000>

Para detener el servidor, vuelve a PowerShell y presiona `Ctrl+C`.

## Prueba rápida

Selecciona **Analizar sentimiento** y prueba con:

```text
La atención fue rápida y amable, pero la instalación se demoró demasiado.
```

Luego cambia la tarea a **Detectar idioma**, **Extraer frases clave**, **Reconocer entidades** o **Detectar información personal (PII)** y prueba con texto de demostración. Evita usar datos reales de personas.

## Seguridad

- La clave se guarda en `.env`, que está excluido de Git mediante `.gitignore`.
- No pegues la clave en el código ni la subas al repositorio.
- La aplicación escucha solo en `127.0.0.1`, para uso local en clase.
- El texto ingresado se envía al recurso de Azure configurado para su análisis.

## Archivos

- `web_app.py`: servidor Flask e integración con Azure AI Language.
- `templates/index.html`: interfaz web para elegir la tarea y ver los resultados.
- `requirements.txt`: dependencias Python.
- `.env.example`: plantilla para configurar el endpoint y la clave.
