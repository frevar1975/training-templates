# Laboratorio: detección de idioma con Azure AI Language

Aplicación en Python que analiza comentarios de prueba y muestra el idioma detectado, el código ISO 639-1 y la confianza del servicio. Incluye demo de consola y página web local.

## Requisitos

- Python 3.10 o posterior
- Visual Studio Code
- Recurso Azure Language activo
- Endpoint y clave de ese mismo recurso

## Preparación en Visual Studio Code

1. Abre la carpeta del proyecto en Visual Studio Code.
2. Abre una terminal en la carpeta del proyecto.
3. Crea y activa el entorno virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

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

   Usa endpoint y clave del mismo recurso. No pegues la clave en el código,
   no la compartas y no subas `.env` al repositorio.

## Demo web local

1. Con el archivo `.env` configurado, inicia la aplicación:

   ```powershell
   python web_app.py
   ```

2. Abre `http://127.0.0.1:5000` en el navegador.
3. Escribe o pega un texto y pulsa **Detectar idioma**.

La página permite mostrar al alumno el texto de entrada y el resultado.
El servidor se limita a la computadora local. La clave permanece en el backend
y no se envía al navegador.

## Demo de consola

También puedes ejecutar la versión de consola con los textos de ejemplo:

```powershell
python app.py
```

## Resultado

- Idioma detectado
- Código ISO 639-1
- Confianza estimada por el servicio

## Seguridad

- `.env` está excluido mediante `.gitignore`.
- Usa solo textos ficticios en la práctica.
- Si una clave se publica por accidente, rótala en Azure.
