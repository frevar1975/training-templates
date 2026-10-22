# Demo web: detección de idioma y reconocimiento de entidades

Aplicación en Python con una página web local para probar dos capacidades de Azure AI Language:

- **Detectar idioma:** muestra el idioma, el código ISO 639-1 y la confianza.
- **Reconocer entidades:** identifica menciones de personas, lugares, organizaciones, fechas y otras categorías en un texto en inglés.

## Requisitos

- PC con Windows
- Python 3.10 o posterior
- Git for Windows
- Visual Studio Code y la extensión Python de Microsoft
- Recurso Azure AI Language activo, con endpoint y clave

## Configuración desde una PC nueva

1. Instala Python desde https://www.python.org/downloads/ y marca **Add python.exe to PATH**.
2. Instala Git desde https://git-scm.com/download/win y VS Code desde https://code.visualstudio.com/.
3. Abre PowerShell y verifica las instalaciones:

   ```powershell
   py --version
   git --version
   ```

4. Clona el repositorio de delivery y entra a la carpeta de la demo:

   ```powershell
   New-Item -ItemType Directory -Force C:\clases
   Set-Location C:\clases
   git clone https://github.com/frevar1975/training-delivery.git
   Set-Location .\training-delivery\AI-901\Netxpress\demo-language-detection-python
   ```

   Para Education IT, la carpeta es `AI-901\EducationIT-octubre-2026\demo-language-detection-python`. Si el repositorio ya está clonado, entra en él y ejecuta `git pull`.

5. Crea el entorno virtual e instala dependencias:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   Si PowerShell bloquea la activación, usa `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` y ejecuta la aplicación con ese mismo Python.

6. Crea la configuración local:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

7. En Azure Portal, abre el recurso **Azure AI Language** y busca **Keys and Endpoint / Claves y punto de conexión**. Completa el archivo `.env` con endpoint y clave de ese mismo recurso:

   ```dotenv
   LANGUAGE_ENDPOINT=https://TU-RECURSO.cognitiveservices.azure.com/
   LANGUAGE_KEY=TU_CLAVE
   ```

   Guarda el archivo. No compartas la clave ni subas `.env` a GitHub.

## Ejecutar la demo

Con el entorno virtual activo:

```powershell
python web_app.py
```

Abre http://127.0.0.1:5000 en el navegador. Selecciona el análisis, escribe o pega el texto y presiona **Analizar texto**.

- Para **Detectar idioma**, prueba frases en español, inglés y francés.
- Para **Reconocer entidades**, usa texto en inglés, por ejemplo: `Alex and I attended a Microsoft AI conference. It was in Las Vegas on September 21st.`

La página muestra categoría y confianza para cada entidad reconocida. Para detener el servidor, vuelve a PowerShell y presiona **Ctrl + C**.

La versión por consola con textos de ejemplo también está disponible mediante `python app.py`.

## Cómo funciona

La página envía el texto al servidor Flask local. Según la opción seleccionada, el servidor llama a `detect_language` o `recognize_entities` del SDK de Azure AI Text Analytics. La clave permanece en el servidor local y no se envía al navegador.

## Solución de problemas

- **`py` o `git` no se reconoce:** reinstala la herramienta; para Python marca **Add python.exe to PATH** y vuelve a abrir PowerShell.
- **No encuentra `templates/index.html`:** ejecuta desde la raíz de la demo, donde está `web_app.py` y la carpeta `templates`.
- **Error de autenticación:** revisa que endpoint y clave sean del mismo recurso Language.
- **La página no abre:** deja activa la terminal donde se ejecuta `python web_app.py`; la aplicación local usa el puerto 5000.

## Seguridad y costos

Usa textos ficticios, no datos personales. Los textos se envían a Azure para analizarlos y el consumo depende del nivel de precios del recurso. La página escucha solo en la PC local (`127.0.0.1`).
