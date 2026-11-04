# AI-3016 · Día 3 · Demos de herramientas en VS Code

Demos para explicar cuatro herramientas de la API de Responses. Están pensados para que el instructor los ejecute y muestre el flujo en pantalla; la clase no necesita programar.

## Qué mostrar

1. **Code Interpreter** — el modelo pide ejecutar un cálculo y obtiene el resultado.
2. **Web Search** — el modelo consulta la web y puede devolver referencias a las fuentes.
3. **File Search** — el modelo busca dentro de una política ficticia cargada a un vector store.
4. **Function calling** — el modelo solicita una función; el programa local la ejecuta y devuelve el resultado. La función de este demo solo consulta disponibilidad ficticia: no realiza reservas.

## Preparación en VS Code (Windows / PowerShell)

1. Instala Python 3.10 o superior y la extensión **Python** de Microsoft para VS Code.
2. Abre esta carpeta en VS Code.
3. En Terminal > New Terminal, crea un entorno e instala dependencias:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copia `.env.example` a `.env` y completa:
   - `FOUNDRY_PROJECT_ENDPOINT`: endpoint del proyecto de Foundry, con forma `https://<recurso>.services.ai.azure.com/api/projects/<proyecto>`.
   - `MODEL_DEPLOYMENT`: nombre exacto de tu deployment, por ejemplo `gpt-5.2`.
   - Usa **una** forma de autenticación:
     - `AZURE_OPENAI_API_KEY`: clave del recurso, si está habilitada para tu proyecto; o
     - inicia sesión con `az login` y deja vacía la clave para usar Microsoft Entra ID.
5. Abre `.vscode/launch.json`; elige una de las cuatro configuraciones y presiona **F5**. También puedes ejecutar el archivo desde la terminal como se indica abajo.

> No subas el archivo `.env` ni compartas claves. El `.gitignore` de esta carpeta lo excluye.

## Ejecución manual

```powershell
python 01_code_interpreter.py
python 02_web_search.py
python 03_file_search.py
python 04_function_calling.py
```

## Guion breve para presentar

- Antes de cada ejecución, pregunta a la clase qué tarea conviene delegar a una herramienta.
- En VS Code, muestra el nombre de la herramienta y el prompt; ejecuta el demo y observa el resultado en la terminal.
- Cierra con la diferencia: el modelo decide cuándo necesita una herramienta, pero la herramienta concreta realiza una tarea especializada.
- En function calling, destaca que el modelo **no ejecutó la acción por su cuenta**: el programa atendió la llamada y devolvió datos. En un sistema real, una acción como reservar o pagar debería requerir validaciones y confirmación.

## Datos y costos

- El archivo de búsqueda contiene una política de viaje **inventada para la clase**; no representa una política real.
- Web Search consulta servicios externos. Code Interpreter y otros servicios pueden generar cargos al usarse; revisa el precio vigente y el presupuesto del proyecto antes de ejecutar.
- File Search crea un vector store temporal. El script lo elimina al terminar; usa `--keep-store` para conservarlo y ver su ID. Si lo conservas, elimínalo después desde el portal o adapta el script para borrarlo.
- Las respuestas del modelo pueden equivocarse. Para decisiones reales, verifica las fuentes y los datos.

## Archivos

| Archivo | Herramienta / propósito |
|---|---|
| `01_code_interpreter.py` | Análisis sencillo de ventas ficticias |
| `02_web_search.py` | Búsqueda web actual y fuentes |
| `03_file_search.py` | Consulta de política ficticia |
| `04_function_calling.py` | Llamada a una función local simulada |
| `common.py` | Cliente y configuración compartidos |
| `demo-data/politica_viajes_demo.txt` | Documento de prueba |
