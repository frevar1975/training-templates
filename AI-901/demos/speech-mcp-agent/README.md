# Demo AI-901: agente de voz con Azure Speech MCP

Un agente en Microsoft Foundry recibe un audio, llama al servidor MCP de Azure Speech para transcribirlo, analiza la consulta y puede generar una respuesta hablada. No hace falta programar ni hospedar un servidor MCP propio: se conecta el servidor remoto **Azure Speech MCP Server** desde el catálogo de herramientas.

## Qué muestra

1. El alumno carga un WAV de prueba en Azure Blob Storage.
2. El agente invoca Speech MCP para transcribirlo.
3. El modelo identifica el motivo y los datos mencionados, y redacta una respuesta sin inventar información.
4. Speech MCP convierte esa respuesta a voz y guarda el WAV de salida en Blob Storage.

**Diferencia con el demo anterior:** allí la aplicación Python llama directamente al SDK de Speech. Aquí el agente descubre e invoca las capacidades de voz mediante MCP.

## Requisitos

- Suscripción de Azure.
- Un recurso de Microsoft Foundry en una región compatible, con Foundry Agent Service y herramientas MCP habilitadas. Microsoft indica que el uso de MCP requiere el nivel Agent Service Enterprise; un recurso protegido por red no es compatible con Speech MCP.
- Un modelo del agente que admita llamadas a herramientas.
- Una cuenta de Azure Storage con un contenedor para los audios. Tu usuario debe poder generar SAS para ese contenedor.
- Un audio corto no sensible. Puedes usar `01-confirmacion-cita-es-BO.wav` o `02-consulta-pedido-es-BO.wav` creados por el demo [Cargar audio y transcribir con Azure Speech](../speech-audio-upload/README.md).

Consulta la documentación oficial para confirmar regiones y requisitos vigentes: [Conectar Azure Speech a un agente](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-ai-speech).

## Preparar Azure Blob Storage

1. En Azure Portal, abre o crea una cuenta de Storage.
2. En **Control de acceso (IAM)**, asigna a tu usuario **Storage Blob Data Contributor**.
3. Crea un contenedor, por ejemplo `speech-audio-demo`.
4. Sube uno de los WAV de prueba.

Para crear el audio, sigue las instrucciones del demo anterior. Ese generador usa las credenciales de un recurso Azure Speech configurado en un archivo local `.env`; no subas ese archivo a GitHub.

## Crear el agente y conectar Speech MCP

1. Abre [Microsoft Foundry](https://ai.azure.com/) y crea un agente.
2. Selecciona un modelo que permita tool calling.
3. Abre **Tools (Herramientas) > Add (Agregar) > Add a new tool (Agregar herramienta) > Catalog (Catálogo)**.
4. Busca **Azure Speech MCP Server**, selecciónalo y pulsa **Create**.
5. Configura la conexión:

   | Campo | Valor |
   |---|---|
   | `foundry-resource-name` | Nombre de tu recurso Microsoft Foundry |
   | `Authorization: Bearer` | KEY1 o KEY2 del recurso Foundry |
   | `X-Blob-Container-Url` | URL SAS del contenedor con permisos de lectura y escritura |

6. Genera la SAS del contenedor con el menor tiempo de expiración práctico y completa la conexión. La herramienta necesita el contenedor para guardar el audio generado por texto a voz.

## Guion para mostrar cómo agregar MCP desde cero

Este guion empieza con un agente nuevo y muestra la conexión de **Azure Speech MCP Server** en Microsoft Foundry. No borres el agente de prueba que ya funciona: crea otro para la demostración. La cuenta de Storage, el contenedor y el recurso Foundry pueden prepararse antes de la clase.

### Antes de compartir la pantalla

Ten listo:

- Un recurso de Microsoft Foundry en una región y nivel que admitan herramientas MCP.
- Un modelo con llamadas a herramientas, por ejemplo GPT-4o.
- Una cuenta de Azure Storage con un contenedor privado y un WAV de prueba ya cargado.
- En Azure Portal, las credenciales del recurso Foundry (**KEY1** o **KEY2**) y una SAS del contenedor con permisos de lectura y escritura para configurar la conexión.
- Una SAS de solo lectura, vigente y de corta duración, para el archivo WAV. Esta es distinta de la SAS del contenedor.

No muestres ni guardes las claves o URL SAS en las diapositivas, capturas ni repositorio.

### Crear el agente y agregar el servidor MCP

1. Abre Microsoft Foundry y selecciona **Build > Agents > Create agent**.
2. Asigna un nombre, por ejemplo `Demo-Speech-MCP-Desde-Cero`, elige GPT-4o (o un modelo compatible con tool calling) y crea el agente.
3. En **Playground > Tools**, selecciona **Add > Add a new tool**.
4. Abre la pestaña **Catalog**, busca **Azure Speech MCP Server**, selecciónalo y pulsa **Create**.
5. En el formulario de conexión:
   - **Name:** conserva `AzureSpeechMCPServer` o escribe un nombre reconocible.
   - **Remote MCP Server endpoint:** verifica el endpoint que propone Foundry.
   - **foundry-resource-name:** escribe el nombre del recurso de Microsoft Foundry; no uses el nombre del proyecto ni el de Storage.
   - **Bearer (API Key):** pega KEY1 o KEY2 obtenida desde **Azure Portal > recurso Foundry > Keys and Endpoint**.
   - **X-Blob-Container-Url:** pega la SAS del contenedor con lectura y escritura para guardar el audio que genere la síntesis de voz.
6. Pulsa **Connect**. Cuando aparezca el cuadro **Configure**, deja **Allowed AzureSpeechMCPServer tools** vacío para permitir las herramientas del servidor.
7. Para que la demostración pida confirmación antes de cada llamada, conserva **Never auto-approve tools** y pulsa **Apply**.
8. Comprueba que **Azure Speech MCP Server** aparezca en la lista **Tools** del agente.

### Probar la transcripción del audio

El Playground no aceptó el WAV adjunto directamente para la llamada MCP. El argumento `audioUrl` debe recibir la URL SAS completa del WAV:

1. En Azure Portal, abre el blob WAV y selecciona **Generate SAS**.
2. Selecciona permiso **Read**, establece un vencimiento corto y genera la URL.
3. Copia el campo **Blob SAS URL** completo. La URL del archivo debe abrir o descargar el WAV en el navegador. No uses solo el nombre del archivo ni la URL del contenedor.
4. En el chat del Playground, envía:

```text
Transcribe el audio ubicado en <URL_SAS_COMPLETA_DEL_WAV>.
Usa español de Bolivia (es-BO), devuelve la transcripción literal,
clasifica el motivo, extrae los datos mencionados e indica los datos faltantes.
No inventes información.
```

5. Si aparece una solicitud de aprobación, revisa que corresponda a `speech_to_text` y apruébala.
6. En **Traces**, confirma que `audioUrl` contiene la URL completa del archivo y revisa el resultado.

La prueba validada transcribió audio en español y clasificó la consulta como `CONFIRMAR_CITA`; extrajo los datos mencionados e indicó que la fecha exacta faltaba porque el audio decía “mañana”.

**Seguridad para la prueba:** la URL SAS es una credencial. Si la pegas en el mensaje del Playground, usa únicamente una SAS temporal del audio de demostración, no sensible; no compartas una captura donde se vea y limpia el historial de prueba al terminar.

### Extensión opcional: generar voz

La conexión tiene la SAS del contenedor para guardar resultados de texto a voz. En el chat, solicita que lea la respuesta en español y comprueba el enlace al WAV generado. Esta parte queda pendiente de validación práctica; verifica el resultado durante la demostración antes de presentarla como probada.

### Solución rápida de problemas

| Síntoma | Qué revisar |
|---|---|
| No se puede adjuntar el WAV en el Playground | Usa la Blob SAS URL del archivo en el pedido al agente. |
| Speech MCP no descarga el audio | Genera una SAS desde el blob WAV con permiso **Read** y vencimiento futuro; confirma que la URL completa descarga el archivo en el navegador. |
| Aparece un XML de Storage al abrir la URL | Vuelve al blob y copia el campo **Blob SAS URL**; no copies la dirección del portal o del contenedor. |
| El agente envía solo el nombre del WAV | Repite el pedido indicando la URL SAS completa del archivo. |
| Falla la conexión MCP | Revisa el nombre del recurso Foundry, KEY1/KEY2 y la SAS de contenedor con lectura y escritura. |
| No aparece una solicitud de aprobación | Revisa **Configure > Approval setting** y selecciona **Never auto-approve tools** para requerir aprobación manual. |

## Instrucciones del agente

Puedes usar estas instrucciones como base:

```text
Eres un asistente de atención al cliente que analiza consultas de voz en español.

Cuando el usuario proporcione la URL de un audio:
1. Usa Azure Speech MCP para transcribir el audio en español.
2. Devuelve la transcripción.
3. Clasifica la consulta como CONFIRMAR_CITA, CONSULTAR_PEDIDO u OTRO.
4. Extrae solo los datos que realmente aparecen en la transcripción. Si falta un dato, indica "No mencionado".
5. Resume la solicitud en una frase y redacta una respuesta breve, cordial y útil.
6. No inventes estados de pedidos, horarios, citas ni políticas de la empresa.
7. Si te piden leer la respuesta, usa Azure Speech MCP para generar audio en español con una voz disponible y comparte el enlace resultante.

Aclara cuando una transcripción o dato no sea seguro.
```

## Probar el reconocimiento de voz

Genera una SAS con permiso de **lectura** para el WAV de prueba y una expiración breve. En el Playground, prueba con una instrucción como:

```text
Transcribe en español el audio de esta URL: <URL_SAS_DEL_WAV>
Después indica el motivo de la consulta, los datos mencionados y una respuesta sugerida. No inventes información.
```

Ejemplo esperado para el audio de pedido:

- **Motivo:** consultar el estado de un pedido.
- **Datos mencionados:** identificador del pedido y solicitud de actualización por correo.
- **Respuesta sugerida:** confirma que se revisará el estado, sin afirmar que el pedido ya fue enviado o entregado.

Verifica en el historial de ejecución que el agente llamó a la herramienta **Azure Speech MCP**.

## Probar la respuesta hablada

En el mismo Playground, pide:

```text
Lee en voz alta la respuesta sugerida en español usando Azure Speech MCP.
```

Speech MCP guarda el WAV generado en el contenedor y el Playground muestra un enlace para escucharlo.

## Resultado de la prueba guiada

La prueba se completó en Microsoft Foundry con un audio de español boliviano. Azure Speech MCP transcribió el audio y el agente clasificó el motivo como `CONFIRMAR_CITA`, extrajo hora, clínica, requisitos y contacto, y señaló correctamente que no podía deducir una fecha exacta a partir de la palabra “mañana”.

### Cómo proporcionar el audio al MCP

El Playground no aceptó el WAV como archivo adjunto para esta llamada. La herramienta `speech_to_text` necesita que `audioUrl` sea una URL accesible al archivo:

1. Sube el WAV a un contenedor privado de Azure Blob Storage.
2. En el blob del audio, selecciona **Generate SAS** y crea una URL SAS con permiso **Read** y vencimiento corto.
3. Copia la **Blob SAS URL** completa del archivo. No uses solo el nombre del WAV, el token SAS suelto, la URL del contenedor ni la dirección de la página del portal.
4. Comprueba la URL en una ventana del navegador. Debe descargar o reproducir el WAV; si aparece un XML de error, vuelve al blob y copia la **Blob SAS URL** generada para ese archivo.
5. En el Playground, incluye esa URL en el pedido:

```text
Transcribe el audio ubicado en <URL_SAS_COMPLETA_DEL_WAV>.
Usa español de Bolivia (es-BO), devuelve la transcripción literal,
clasifica el motivo, extrae los datos mencionados e indica los datos faltantes.
No inventes información.
```

En **Traces**, confirma que la llamada a `speech_to_text` contiene la URL completa en `audioUrl`. Si Foundry pide aprobación, revisa la llamada y apruébala. Para pedir aprobación manual en la configuración de la herramienta, selecciona **Never auto-approve tools**.

### Resultado esperado

Para el audio de confirmación de cita, el agente debe:

- devolver la transcripción en español;
- clasificar el motivo como `CONFIRMAR_CITA`;
- extraer los datos expresados en el audio;
- marcar la fecha exacta como faltante cuando el audio solo dice “mañana”;
- redactar una respuesta sugerida sin agregar datos no mencionados.

La prueba de transcripción y análisis quedó validada. La generación de una respuesta hablada es un paso opcional posterior: se solicita en el chat y el archivo de salida se guarda en el contenedor configurado. Valídala por separado antes de presentar la síntesis de voz como probada.

### Solución del error de descarga

Si Speech MCP informa que no puede descargar el audio, verifica que:

- `audioUrl` sea la **Blob SAS URL completa del WAV**, no solo el nombre;
- la SAS corresponda al blob correcto, esté vigente y tenga permiso **Read**;
- al abrirla en el navegador se descargue el audio;
- no se haya copiado una URL del portal o del contenedor por error.

## Seguridad y limpieza

- Usa solo audios de prueba, sin datos personales o información de clientes.
- Una URL SAS es una credencial temporal. Usa permisos mínimos y expiración corta; no la guardes en archivos del repositorio, capturas ni prompts permanentes.
- No publiques KEY1/KEY2 ni SAS en GitHub. Si una clave se expone, rótala.
- Al terminar, elimina el agente y los audios de prueba si ya no los necesitas. Las SAS expiran según el plazo configurado.

## Solución de problemas

| Problema | Qué revisar |
|---|---|
| No aparece Azure Speech MCP Server | Comprueba región y nivel de servicio del recurso Foundry; MCP requiere Agent Service Enterprise. |
| El agente no llama a Speech MCP | Confirma que la herramienta aparezca conectada y que el modelo admita tool calling. Pide explícitamente que transcriba el audio con la herramienta. |
| Error de acceso al WAV | La SAS del archivo debe estar vigente y permitir lectura. |
| No aparece el WAV de voz generado | Revisa que la SAS del contenedor configurada en la conexión permita lectura y escritura. |
| Error de autorización al conectar el MCP | Verifica KEY1/KEY2 y el nombre del recurso Foundry. |

## Referencias oficiales

- [Conectar Azure Speech en Foundry Tools a un agente](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-ai-speech)
- [Módulo Microsoft Learn: desarrollar un agente de voz con Speech MCP](https://learn.microsoft.com/training/modules/develop-speech-agent-speech-mcp/)
