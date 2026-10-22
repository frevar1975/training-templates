# Demo web: detección de idioma con Azure AI Language

Guía para ejecutar esta práctica desde una PC Windows nueva. El alumno escribe un texto en el navegador y ve el idioma detectado, el código ISO 639-1 y la confianza.

## 1. Instalar las herramientas

Instala en la PC:

- **Python 3.10 o posterior**, desde https://www.python.org/downloads/
  - Durante la instalación, marca **Add python.exe to PATH**.
- **Git for Windows**, desde https://git-scm.com/download/win
- **Visual Studio Code**, desde https://code.visualstudio.com/
- En VS Code, instala la extensión **Python** de Microsoft.

Cierra y vuelve a abrir PowerShell después de instalar Python y Git.

Comprueba las instalaciones:

```powershell
py --version
git --version
```

Los comandos deben mostrar versiones instaladas. Si `py` no se reconoce, vuelve a instalar Python marcando **Add python.exe to PATH**.

## 2. Descargar el repositorio

Para la clase de Netxpress, clona el repositorio de delivery:

```powershell
New-Item -ItemType Directory -Force C:\clases
Set-Location C:\clases
git clone https://github.com/frevar1975/training-delivery.git
```

Si ya tienes el repositorio, actualízalo en vez de clonarlo otra vez:

```powershell
Set-Location C:\clases\training-delivery
git pull
```

Abre la carpeta de esta demo:

```powershell
Set-Location C:\clases\training-delivery\AI-901\Netxpress\demo-language-detection-python
code .
```

Si `code .` no funciona, abre VS Code y selecciona esa carpeta desde **Archivo → Abrir carpeta**.

La demo también está en estos repositorios:

- Plantilla: `training-templates\AI-901\demos\language-detection-python`
- Delivery Education IT: `training-delivery\AI-901\EducationIT-octubre-2026\demo-language-detection-python`

## 3. Crear el entorno e instalar dependencias

En la terminal PowerShell de VS Code, verifica que estás dentro de la carpeta `demo-language-detection-python`. Luego ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, no cambies la política del equipo. Ejecuta pip usando directamente el Python del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Configurar Azure AI Language

Crea el archivo local `.env` copiando el ejemplo y ábrelo:

```powershell
Copy-Item .env.example .env
notepad .env
```

En Azure Portal, abre el recurso **Azure AI Language** y busca **Keys and Endpoint / Claves y punto de conexión**. Copia el endpoint y una clave de ese mismo recurso dentro de `.env`:

```dotenv
LANGUAGE_ENDPOINT=https://TU-RECURSO.cognitiveservices.azure.com/
LANGUAGE_KEY=TU_CLAVE
```

Guarda y cierra el archivo. No pegues la clave en el código, no la compartas ni subas `.env` a GitHub. El archivo está excluido por `.gitignore`.

## 5. Iniciar y probar la página

Si activaste `.venv`, inicia el servidor así:

```powershell
python web_app.py
```

Si no pudiste activar el entorno:

```powershell
.\.venv\Scripts\python.exe web_app.py
```

Abre en el navegador http://127.0.0.1:5000, escribe una frase y pulsa **Detectar idioma**. Prueba, por ejemplo, una frase en español, otra en inglés y otra en francés. Para detener la aplicación, vuelve a PowerShell y presiona **Ctrl + C**.

## 6. Qué hace la aplicación

1. El navegador envía el texto a la aplicación Flask que corre en la PC.
2. Flask llama a Azure AI Language con el SDK de Python.
3. El servicio responde con el idioma y la confianza.
4. La página muestra el idioma, el código ISO 639-1 y la confianza.

La demo de consola opcional está en `app.py`; ejecútala con `python app.py` usando el entorno virtual.

## Solución de problemas

- **`py` o `git` no se reconoce:** instala la herramienta correspondiente, marca Python en PATH y vuelve a abrir PowerShell.
- **No se encuentra `templates/index.html`:** abre la carpeta raíz de esta demo, donde están `web_app.py`, `requirements.txt` y la carpeta `templates`.
- **Error de configuración:** confirma que guardaste `.env` junto a `web_app.py` y que las variables están escritas como `LANGUAGE_ENDPOINT` y `LANGUAGE_KEY`.
- **Error de autenticación o recurso:** confirma que la clave y el endpoint pertenecen al mismo recurso Azure AI Language.
- **La página no carga:** confirma que la terminal sigue mostrando el servidor activo en el puerto 5000.

## Seguridad y costos

Usa textos ficticios, no información personal. El texto se envía a Azure para su análisis y el uso puede generar consumo según el nivel de precios del recurso. La aplicación escucha solo en la PC local (`127.0.0.1`).
