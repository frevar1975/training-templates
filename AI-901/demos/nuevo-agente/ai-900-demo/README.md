# Demo de interacción con un agente de Microsoft Foundry

Demo de AI-901: aplicación Flask con una página de chat que envía mensajes a un agente de Microsoft Foundry y muestra sus respuestas.

El código ya está preparado. Para reutilizarlo con otro agente solo se cambian los valores del archivo `.env`.

## 1. Clonar el repositorio

Abre PowerShell y ejecuta:

```powershell
cd C:\clases
mkdir demomiercoles-borrar
cd demomiercoles-borrar
git clone https://github.com/frevar1975/training-templates.git
cd .\training-templates\AI-901\demos\nuevo-agente\ai-900-demo
```

Si el directorio de trabajo ya existe, cambia únicamente a la carpeta del demo:

```powershell
cd C:\clases\demomiercoles-borrar\training-templates\AI-901\demos\nuevo-agente\ai-900-demo
```

## 2. Crear el entorno virtual

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Cuando aparezca `(.venv)` al inicio de la línea, el entorno está activo.

## 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 4. Crear la configuración local

Copia el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
notepad .env
```

Completa los valores del proyecto y del agente:

```env
PROJECT_ENDPOINT=https://<endpoint-del-proyecto>
AGENT_REFERENCE=<referencia-del-agente>
```

Cada alumno debe usar sus propios valores. El archivo `.env` es local y no debe subirse a GitHub.

## 5. Iniciar sesión en Azure

La aplicación utiliza `DefaultAzureCredential`. Inicia sesión con Azure CLI:

```powershell
az login
```

Si tienes varias suscripciones, selecciona la correcta:

```powershell
az account set --subscription "<nombre-o-id-de-suscripcion>"
```

## 6. Ejecutar la aplicación

```powershell
python app.py
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

## 7. Probar el agente

1. Escribe un mensaje en el cuadro de chat.
2. Envía la pregunta.
3. Verifica que la respuesta corresponda a las instrucciones del agente creado en Foundry.
4. Cambia `AGENT_REFERENCE` por la referencia de otro agente y vuelve a probar.

## Estructura del proyecto

```text
ai-900-demo/
├── app.py
├── .env.example
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── styles.css
└── .vscode/
    └── launch.json
```

## Solución rápida de problemas

### `ModuleNotFoundError`

Confirma que el entorno virtual esté activo y ejecuta:

```powershell
pip install -r requirements.txt
```

### Error de autenticación

Ejecuta:

```powershell
az login
az account show
```

### Error de endpoint o agente

Revisa que `.env` contenga:

- El endpoint correcto del proyecto.
- La referencia correcta del agente.
- Sin comillas adicionales.
- Sin espacios al inicio o al final.

### El puerto está ocupado

Ejecuta Flask en otro puerto o cierra la aplicación anterior antes de volver a iniciar el demo.
