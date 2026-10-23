# Demo AI-901: cargar audio y transcribir con Azure Speech

Aplicación web local para cargar un archivo de audio, convertirlo a WAV PCM y transcribirlo con Azure Speech SDK. Permite probar reconocimiento de voz en español boliviano y otros idiomas.

## Qué muestra

1. El alumno carga un archivo de audio desde el navegador.
2. La app normaliza el formato con FFmpeg y configura el idioma elegido.
3. Azure Speech devuelve el texto reconocido.
4. El alumno copia o descarga la transcripción y compara el resultado con el audio.

## Requisitos

- Windows 10/11 y Python 3.10 o superior.
- FFmpeg disponible en `PATH`. En Windows se puede instalar con `winget install Gyan.FFmpeg`; luego reinicia PowerShell.
- Un recurso Azure Speech y su clave y región.

## Descargar y ejecutar en Windows PowerShell

Si todavía no tienes el repositorio de cursos:

```powershell
Set-Location C:\clases
git clone https://github.com/frevar1975/training-templates.git
Set-Location .\training-templates\AI-901\demos\speech-audio-upload
```

Si ya lo tienes clonado, actualízalo y entra al demo:

```powershell
Set-Location C:\clases\training-templates
git pull --ff-only
Set-Location .\AI-901\demos\speech-audio-upload
```

Prepara el entorno e instala los requisitos:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Completa `.env` con los datos del recurso Speech (no Azure Language):

```text
SPEECH_KEY=tu_clave
SPEECH_REGION=eastus
FLASK_SECRET_KEY=demo-local
```

Guarda el archivo. No compartas `.env` ni lo subas a GitHub.

## Generar los audios de prueba

Con `.env` configurado y el entorno virtual activo, ejecuta:

```powershell
py generar_audios_es.py
```

Se crean dos WAV de prueba con voces neuronales de español boliviano y sus transcripciones de referencia: una confirmación de cita y una consulta por un pedido. Los archivos se guardan en esta carpeta y se pueden cargar en la misma app.

## Iniciar la aplicación

```powershell
py app.py
```

Abre <http://127.0.0.1:5000>, selecciona **Español (Bolivia)** y carga uno de los WAV generados. Detén el servidor con `Ctrl+C`.

## Formatos de audio

WAV, MP3, M4A, MP4, OGG, WEBM y FLAC. La app convierte el audio a WAV PCM mono de 16 kHz para enviarlo al Speech SDK. La carga máxima es 25 MB. Para una demostración breve, usa audios de menos de 30 segundos.

## Seguridad y funcionamiento

- `.env`, `.venv/` y archivos temporales están excluidos de Git. `.env.example` contiene solo nombres de variables y valores de muestra.
- La aplicación escucha solo en `127.0.0.1`, para uso local en clase.
- Los archivos cargados se guardan en un directorio temporal y se eliminan al terminar la solicitud. El audio se envía al recurso Azure Speech configurado para su procesamiento.
- La transcripción puede requerir corrección, especialmente con nombres propios, ruido o acentos.
- Esta versión usa `recognize_once_async`, orientada a audio breve.

## Archivos

- `app.py`: aplicación Flask e integración con Azure Speech SDK.
- `generar_audios_es.py`: genera audios de prueba en español boliviano con el recurso configurado.
- `templates/index.html`: interfaz web de carga y resultados.
- `.env.example`: plantilla de configuración sin credenciales.
- `requirements.txt`: dependencias de Python.
