# AB-730 Día 6 — Demos individuales de informe y métricas

Este paquete reúne tres ejercicios autónomos para convertir información de trabajo en un informe con Copilot. Los escenarios, personas, empresas, tareas, pedidos, fechas y cifras son ficticios.

## Demo 1 — Outlook a Word

**Flujo:** correo de estado en Outlook → resumen y verificación con Copilot → informe editable en Word.

- Fuente para preparar el mensaje de práctica: `template/05-correo-demo1-atlas.txt`.
- Guía paso a paso: `delivery/Guia_Demo_1_Outlook_a_Word.docx`.
- Respuesta modelo: `delivery/Resultado_esperado_Demo1.md`.
- Duración completa sugerida: 50 minutos.

El correo se puede enviar al buzón de prueba o pegar en Copilot Chat como contingencia. Si se pega manualmente, el instructor debe aclarar que no se está demostrando recuperación automática desde Outlook.

## Demo 2 — Chat de pedidos a informe mensual

**Flujo:** conversación ficticia → análisis en Copilot Chat o agente Analista si está disponible → informe mensual en Word.

- Fuente de práctica: `template/06-chat-ficticio-zapateria-paso-firme.txt`.
- Guía paso a paso: `delivery/Guia_Demo_2_Chat_a_Informe_Word.docx`.
- Respuesta modelo: `delivery/Resultado_esperado_Demo2.md`.
- Duración completa sugerida: 55 minutos.

El ejercicio usa contenido pegado manualmente. No conecta Copilot a WhatsApp ni demuestra búsqueda automática en Teams. La diapositiva original describe un canal de Teams y una reunión; el chat de zapatería adapta la secuencia de consolidación, análisis y redacción a un caso comercial.

## Demo 3 — Excel, análisis y Word

**Flujo:** rastreador compartido en Excel → gráfico semanal y análisis de anomalías → sección de métricas en Word.

- Libro de práctica: `template/07-rastreador-progreso-nebula-demo.xlsx`.
- Plantilla de informe: `template/08-informe-semanal-nebula-base.docx`.
- Guía paso a paso: `delivery/Guia_Demo_3_Excel_Analista_Word.docx`.
- Respuesta modelo: `delivery/Resultado_esperado_Demo3.md`.
- Duración completa sugerida: 45 minutos.

La tasa se define como tareas completadas divididas por tareas planificadas para esa semana. El gráfico se deja para crearlo durante el demo con Copilot en Excel. El instructor verifica que el gráfico tenga vínculo con la tabla.

## Qué demuestra cada ejercicio

| Demo | Fuente principal | Trabajo de Copilot | Salida |
|---|---|---|---|
| 1 | Correo de estado del proyecto | Extraer actualizaciones y separar hechos confirmados de estimaciones | Informe semanal del Proyecto Atlas |
| 2 | Conversación mensual de pedidos | Clasificar pedidos, cambios y consultas; reconocer límites de los datos | Informe mensual de Zapatería Paso Firme |
| 3 | Rastreador de tareas | Calcular y visualizar tasas semanales, detectar caída y revisar filas de respaldo | Sección de métricas del Proyecto Nébula |

Los tres demos individuales pueden ejecutarse sin Copilot Studio. Para configurar un agente Standard reutilizable que enrute entre los tres escenarios, consulta la [guía del agente de Copilot Studio](../../dia-06-agente-copilot-studio/README.md).

## Agenda intensiva sugerida para 150 minutos

- Demo 1, versión breve: 35 min.
- Demo 2, versión breve: 35 min.
- Pausa y transición: 10 min.
- Demo 3: 45 min.
- Comparación de resultados, revisión de fuentes y cierre: 25 min.

**Total: 150 minutos.** Las guías completas de los demos 1 y 2 son más extensas; en la versión intensiva se priorizan los prompts principales y la verificación crítica.

## Estructura

- `template/`: fuentes de práctica y documento base para los alumnos.
- `delivery/`: guías del instructor, resultados esperados e índice del paquete.
