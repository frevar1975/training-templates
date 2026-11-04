# AB-730 Día 6 — Agente de Copilot Studio para tres demos

Este paquete permite construir y demostrar un agente **Standard** de Copilot Studio con tres fuentes ficticias independientes. El agente enruta preguntas al ejemplo correspondiente, resume información, separa hechos de interpretaciones y señala límites de los datos.

## Escenarios incluidos

| Demo | Fuente de conocimiento | Qué se practica | Límite que se debe explicar |
|---|---|---|---|
| 1. Proyecto Atlas | `template/01-correo-proyecto-atlas.txt` | Extraer avances, bloqueos, responsables y fechas; redactar un informe verificable | El agente analiza el archivo cargado; no está conectado al buzón de Outlook ni envía correos. |
| 2. Zapatería Paso Firme | `template/02-chat-zapateria-paso-firme.txt` | Convertir conversación ficticia en un resumen mensual de pedidos y seguimiento | No conecta WhatsApp ni calcula ingresos sin precios. |
| 3. Proyecto Nébula | `template/03-rastreador-progreso-nebula.xlsx` | Consultar tasas semanales, detectar cambios y explicar limitaciones | El agente puede analizar datos si los recupera, pero no genera ni inserta un gráfico dentro del Excel. |

## Archivos

- `template/`: tres fuentes ficticias que se cargan directamente como conocimiento y un archivo de instrucciones para copiar al agente. **No cargues las instrucciones como conocimiento**; pégalas en el campo Instrucciones.
- `delivery/Guia_del_instructor_Agente_Copilot_Studio.docx`: preparación, configuración clic a clic, frases para decir, prompts de prueba, respuestas esperadas, agenda, solución de problemas y cierre.
- `delivery/Resultados_esperados_y_validacion.md`: clave breve para revisar las respuestas.

## Preparación rápida

1. Crea un agente nuevo en Copilot Studio con tipo **Standard** y lenguaje español.
2. Pega el contenido de `template/04-instrucciones-del-agente.txt` en **Instructions / Instrucciones**.
3. En **Knowledge / Conocimiento**, carga individualmente los tres archivos de ejemplo. Nómbralos de forma descriptiva y conserva sus descripciones.
4. Guarda y prueba cada demo por separado en el panel de prueba usando los prompts de la guía.
5. Comprueba que cada respuesta use la fuente correcta y no mezcle escenarios.

Las etiquetas exactas de navegación pueden variar con la versión de Copilot Studio. Si no aparece una pestaña en la página inicial, abre el agente y busca **Knowledge** en su menú de configuración.

## Prompt inicial recomendado

> Quiero probar el Demo 1 del Proyecto Atlas. Resume únicamente el correo de Atlas en avances, trabajo en curso, bloqueos y próximos pasos. Distingue hechos explícitos de interpretaciones, conserva las fechas y responsables, señala los datos no especificados y no mezcles información de los otros ejemplos.

## Criterios de éxito

- El agente pregunta qué demo usar cuando el pedido es ambiguo.
- Atlas, Zapatería y Nébula quedan claramente separados.
- Los datos clave y sus matices se conservan.
- Las respuestas declaran cuando falta información.
- El instructor explica con precisión que el agente trabaja con archivos de conocimiento cargados; no consulta Outlook, WhatsApp o Excel en vivo.

## Estructura

- `template/`: fuentes e instrucciones para configurar el agente.
- `delivery/`: guía docente y clave de revisión.
