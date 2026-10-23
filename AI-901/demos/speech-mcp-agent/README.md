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
