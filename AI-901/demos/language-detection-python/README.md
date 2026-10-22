# Laboratorio: detección de idioma con Azure AI Language

Aplicación de consola en Python que analiza comentarios ficticios de clientes
y muestra el idioma detectado, su código ISO 639-1 y la confianza del servicio.

## Requisitos

- Python 3.10 o posterior
- Visual Studio Code
- Recurso Azure Language activo
- Endpoint y clave de ese mismo recurso

## Preparación en Visual Studio Code

1. Extrae la carpeta y ábrela en Visual Studio Code.
2. Abre una terminal en la carpeta del proyecto.
3. Crea y activa el entorno virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, usa `.venv\Scripts\python.exe`
   para ejecutar Python y pip sin activar el entorno.

4. Instala las dependencias:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Copia `.env.example` y nombra la copia `.env`.
6. Abre `.env` y reemplaza los valores de ejemplo:

   ```dotenv
   LANGUAGE_ENDPOINT=https://TU-RECURSO.cognitiveservices.azure.com/
   LANGUAGE_KEY=TU_CLAVE
   ```

   Usa endpoint y clave del mismo recurso. No pegues la clave en `app.py`,
   no la compartas y no subas `.env` al repositorio.

7. Ejecuta:

   ```powershell
   python app.py
   ```

## Qué muestra el resultado

- Idioma detectado
- Código ISO 639-1
- Confianza estimada por el servicio

Los textos de prueba están en `sample_texts` dentro de `app.py`. Puedes
editarlos o agregar comentarios ficticios para comparar resultados.

## Guion breve para la demo

1. El programa carga endpoint y clave desde variables de entorno.
2. El SDK crea un cliente para Azure Language.
3. `detect_language` envía los textos para su análisis.
4. Azure devuelve idioma, código y puntuación de confianza.
5. La detección es una predicción y se debe revisar en aplicaciones sensibles.

## Seguridad

- `.env` está excluido mediante `.gitignore`.
- No uses datos reales de clientes en esta práctica.
- Si una clave se publica por accidente, rótala en Azure.
