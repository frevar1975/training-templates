# Demo 6 — Simular un agente con aprobación humana

**Tiempo:** 15–20 min · **Herramienta:** Copilot Chat + ficha de revisión · **Slides sugeridas:** 17–19 · **Objetivo:** mostrar la diferencia entre sugerir, proponer para aprobación y ejecutar.

## Preparación

Usá el Caso C o B del archivo `template/01-reclamos-ficticios.txt`. Abrí `template/05-ficha-aprobacion-humana.csv`. Explicá que es una simulación, no una integración real.

## Ejecución

1. Prompt: **“Analizá este reclamo. Devolvé un resumen, prioridad sugerida, información faltante y un borrador de respuesta. No inventes datos ni afirmes que registraste o escalaste el reclamo.”**
2. Revisá la salida con toda la clase.
3. Una persona actúa como agente de atención y otra como supervisora. La supervisora completa la ficha: aprobar, corregir, rechazar o escalar.
4. Preguntá qué cambiaría si la IA pudiera consultar el sistema de reclamos o enviar la respuesta sin revisión.
5. Relacioná las respuestas con tres niveles: asiste; prepara y espera aprobación; ejecuta dentro de límites y permisos.

## Cierre y límite

Copilot Chat solo redacta una propuesta; no registra el caso ni envía el mensaje. Un agente conectado necesitaría herramientas, permisos, controles, registros y una política de escalamiento.
