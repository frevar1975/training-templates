# AI-3016 · Día 3 · Demos de herramientas en VS Code

Una demo interactiva permite elegir la herramienta y escribir consultas propias. Los scripts individuales siguen disponibles como ejemplos guiados. La clase puede observar el flujo: no necesita programar.

## Menú interactivo

Abre la carpeta en VS Code, prepara el entorno siguiendo la sección siguiente y ejecuta:

```powershell
python demo_interactivo.py
```

El menú permite seleccionar:

1. **Code Interpreter** — ejecuta cálculos y análisis.
2. **Web Search** — busca información en la web y muestra referencias.
3. **File Search** — responde con base en la política ficticia incluida en `demo-data`.
4. **Function calling** — el modelo solicita una función local; la aplicación la ejecuta y devuelve el resultado.
0. Salir.

Después de elegir, escribe una consulta en la terminal y presiona **Enter**. Puedes usar estos prompts de prueba (copia solo el texto dentro del bloque):

| Opción | Prompt listo para pegar | Qué observar |
|---|---|---|
| **1. Code Interpreter** | `Calcula el total y el promedio mensual de estas ventas: enero 120000, febrero 155000 y marzo 141000 pesos argentinos. Explica brevemente el resultado y muestra las operaciones.` | El modelo puede pedir la herramienta para hacer el cálculo; revisa la respuesta y el indicador de invocación. |
| **2. Web Search** | `Busca tres actividades turísticas para hacer este fin de semana en Buenos Aires. Resume cada una e incluye las fuentes y fechas.` | La respuesta debe incluir fuentes web; abre una y comprueba que respalde el dato. |
| **3. File Search** | `Según la política de viajes del documento, ¿con cuánta anticipación debo solicitar un cambio de reserva y cuál es el límite diario para comida? Indica también qué comprobante se necesita para el reembolso.` | Contrasta la respuesta con `demo-data/politica_viajes_demo.txt`. Luego prueba: `¿La política permite reembolsar excursiones? Si el documento no lo dice, indícalo.` |
| **4. Function calling** | `Consulta si hay disponibilidad para una visita guiada en Buenos Aires el 2026-11-14 a las 10:00 para 2 personas. No hagas una reserva.` | Observa los argumentos que el modelo entrega, la respuesta de la función local y la respuesta final. La disponibilidad es ficticia; no se reserva nada. |

**Cómo probar cada opción:** ejecuta `python demo_interactivo.py`, escribe el número de opción en `Opción:`, pega el prompt correspondiente cuando aparezca `Escribe tu consulta` y presiona **Enter**. Al terminar, el menú vuelve a aparecer. Presiona `0` para salir.

En VS Code, también puedes elegir **Día 3 · Menú interactivo** en Run and Debug y presionar **F5**.

## Preparación en VS Code (Windows / PowerShell)

1. Instala Python 3.10 o superior y la extensión **Python** de Microsoft para VS Code.
2. Abre esta carpeta en VS Code.
3. En Terminal > New Terminal, crea el entorno e instala dependencias:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copia `.env.example` a `.env` y completa:
   - `FOUNDRY_PROJECT_ENDPOINT`: endpoint del proyecto de Foundry, con forma `https://<recurso>.services.ai.azure.com/api/projects/<proyecto>`.
   - `MODEL_DEPLOYMENT`: nombre exacto del deployment, por ejemplo `gpt-5.2`.
   - Usa una forma de autenticación:
     - `AZURE_OPENAI_API_KEY`: clave del recurso, si está habilitada; o
     - inicia sesión con `az login` y deja vacía la clave para usar Microsoft Entra ID.
5. No subas `.env` ni compartas claves. El `.gitignore` de esta carpeta excluye ese archivo.

## Ejemplos guiados

```powershell
python 01_code_interpreter.py
python 02_web_search.py
python 03_file_search.py
python 04_function_calling.py
```

## Guion breve para presentar

- Pide a la clase que elija una herramienta según la necesidad.
- Escribe una consulta sugerida por el grupo y observa la salida.
- En Function calling, muestra el orden: el modelo pide la función, la aplicación ejecuta el código y el modelo redacta la respuesta final.
- Aclara que el modelo no ejecuta por sí solo acciones externas. Una acción real, como reservar o pagar, debería tener validaciones y confirmación.

## Datos y costos

- El archivo de búsqueda contiene una política de viaje inventada para la clase.
- Web Search consulta servicios externos. Code Interpreter y otros servicios pueden generar cargos; revisa el precio vigente y el presupuesto del proyecto antes de ejecutar.
- File Search crea un vector store temporal y lo elimina al salir. Usa `python demo_interactivo.py --keep-store` para conservarlo; elimínalo después desde el portal.
- Las respuestas del modelo pueden equivocarse. Verifica fuentes y datos antes de usarlos.

## Archivos

| Archivo | Propósito |
|---|---|
| `demo_interactivo.py` | Menú para seleccionar herramienta y escribir consultas |
| `01_code_interpreter.py` | Ejemplo guiado de análisis de ventas ficticias |
| `02_web_search.py` | Ejemplo guiado de búsqueda web |
| `03_file_search.py` | Ejemplo guiado de búsqueda en la política ficticia |
| `04_function_calling.py` | Ejemplo guiado de función local simulada |
| `common.py` | Cliente y configuración compartidos |
