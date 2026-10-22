# Laboratorio web de análisis de texto con Azure AI Language

Aplicación educativa en Python y Flask para escribir o pegar texto, elegir una tarea y ver el resultado de Azure AI Language.

## Tareas disponibles

- **Detectar idioma:** idioma, código ISO 639-1 y confianza.
- **Detectar información personal (PII):** valores detectados y texto con esos valores ocultos.
- **Extraer frases clave:** conceptos principales detectados.
- **Reconocer entidades:** personas, organizaciones, lugares, fechas y otras categorías.
- **Analizar sentimiento:** sentimiento general y puntuaciones positivo, neutral y negativo.
- **Resumen introductorio:** presenta frases clave como ideas principales. Esta opción es didáctica y **no llama al servicio dedicado de resumen generativo**.

## Requisitos

- Windows 10/11.
- Python 3.10 o posterior.
- Git for Windows.
- Recurso Azure AI Language activo con endpoint y clave.

## Preparación desde una PC nueva

1. Instala Python desde https://www.python.org/downloads/ (marca **Add python.exe to PATH**), Git desde https://git-scm.com/download/win y Visual Studio Code desde https://code.visualstudio.com/.
2. Abre PowerShell y confirma las instalaciones:

   ```powershell
   py --version
   git --version
   ```

3. Clona este repositorio y entra en la carpeta de la demo:

   ```powershell
   New-Item -ItemType Directory -Force C:\\clases
   Set-Location C:\\clases
   git clone https://github.com/frevar1975/training-templates.git
   Set-Location .\\training-templates\AI-901\demos\language-detection-python
   ```

   Si ya tienes el repositorio, ejecuta `git pull` antes de seguir.

4. Crea un entorno virtual e instala las dependencias:

   ```powershell
   py -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   Si PowerShell impide activar el entorno, ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y vuelve a activar.

5. Crea la configuración local:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

6. En `.env`, pega el endpoint y una clave del mismo recurso **Azure AI Language**:

   ```dotenv
   LANGUAGE_ENDPOINT=https://TU-RECURSO.cognitiveservices.azure.com/
   LANGUAGE_KEY=TU_CLAVE
   ```

   Guarda el archivo. No compartas la clave ni subas `.env` a GitHub.

## Ejecutar

Desde PowerShell, en la raíz de esta demo:

```powershell
python web_app.py
```

Abre http://127.0.0.1:5000, selecciona una tarea, pega el texto y pulsa **Analizar texto**. Para detener el servidor presiona **Ctrl+C** en PowerShell.

## Texto para probar

Puedes usar este texto de ficción en inglés para probar idioma, frases clave, entidades y sentimiento:

```text
Alex and Maria attended a Microsoft AI conference in Las Vegas on September 21st. They loved the practical sessions, but the event organization was confusing.
```

Para probar detección de PII, usa datos ficticios, por ejemplo:

```text
Contact Ana Pérez at ana.demo@example.com or call 555-0100 about the training in Santa Cruz.
```

## Cómo funciona

Flask recibe el texto y la opción seleccionada. El servidor llama a la operación correspondiente del SDK `azure-ai-textanalytics`; las credenciales permanecen en el backend local y no se envían al navegador.

## Solución de problemas

- **404 Resource not found:** confirma que el endpoint y la clave sean del recurso Azure AI Language, no del endpoint del proyecto Foundry ni de un despliegue de modelo.
- **Error de autenticación:** endpoint y clave deben pertenecer al mismo recurso.
- **No encuentra `templates/index.html`:** ejecuta `python web_app.py` desde la raíz de la demo.
- **La página no abre:** deja PowerShell ejecutando la app y revisa que el puerto 5000 esté libre.

## Seguridad

Usa solo texto de demostración. El contenido se envía al servicio Azure configurado. La aplicación escucha únicamente en `127.0.0.1`; no está preparada para producción.
