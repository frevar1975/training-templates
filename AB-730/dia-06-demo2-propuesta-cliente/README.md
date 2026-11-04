# Demo 2 — De fuentes dispersas a una propuesta de cliente

**Curso:** AB-730T00 · **Día:** 6 · **Duración sugerida:** 45–60 min · **Herramientas:** Copilot Chat, Word y PowerPoint

## Para qué sirve

Este ejercicio muestra un flujo de trabajo completo para convertir un pedido urgente y tres fuentes diferentes en una propuesta revisable y una presentación para cliente:

1. **Copilot Chat:** sintetiza notas, correos y una hoja de precios adjuntados en la conversación.
2. **Word:** organiza el análisis verificado en un documento base con estructura y títulos.
3. **PowerPoint:** crea una presentación a partir del documento base; se revisan cifras, supuestos y afirmaciones antes de usarla.

Se presenta después de los demos individuales. En el siguiente bloque, un agente podrá reutilizar instrucciones y estructura para guiar tareas similares. Aquí se ejecuta manualmente cada etapa para que la clase vea qué aporta cada aplicación.

## El escenario

Miércoles, 12:45. Shane recibe por Teams un pedido para preparar una propuesta antes de la reunión de las 15:00. Tiene notas de descubrimiento, correos de Operaciones y Finanzas y una hoja de precios. El cliente ficticio Horizonte Logística SRL quiere comparar un piloto para 15 y 30 usuarios, pero aún debe confirmar usuarios, revisión de TI y condiciones comerciales.

## Archivos descargables

En `template/` están los tres archivos que usa el alumno:

- `01-brief-y-notas-descubrimiento.txt`
- `02-correos-horizonte-logistica.txt`
- `03-pricing-propuesta-horizonte.xlsx`

## Flujo de la demo

1. Descarga la carpeta `template/` o los tres archivos indicados.
2. Inicia Copilot Chat y adjunta los tres archivos.
3. Ejecuta los prompts del [paso a paso del instructor](delivery/Guia_del_instructor.docx), verificando datos, cálculos y asuntos pendientes.
4. Pide una propuesta estructurada y prepara el documento base en Word.
5. Abre PowerPoint y usa Copilot para generar una presentación desde ese documento de Word. La disponibilidad de creación desde archivo depende de licencia, versión y configuración del tenant.
6. Revisa las diapositivas con la lista de control de la guía antes de presentar.

## Estructura recomendada de la presentación

Una presentación de 8 diapositivas: objetivo de la reunión; contexto; problema y evidencia; propuesta de piloto; alcance y etapas relativas; métricas a acordar; alternativas de inversión; decisiones y siguientes pasos. Los datos que son estimaciones deben seguir identificados como tales.

## Límites para una demo responsable

- Los precios, personas y empresa son ficticios y no constituyen una cotización.
- El libro calcula 3 meses de suscripción más una implementación única; impuestos excluidos.
- La reducción de las 3 horas semanales no es un resultado demostrado. Primero se debe establecer una línea base y acordar medición.
- No se deben inventar integraciones, fechas de inicio, ROI, ahorros garantizados ni aprobaciones.
- La revisión de TI, la confirmación de usuarios y la cotización formal quedan como pasos pendientes.

## Variantes de ejecución

- **PowerPoint con creación desde archivo disponible:** generar desde el Word revisado y seleccionar una plantilla autorizada.
- **La opción no aparece:** pedir a Copilot que redacte el contenido por diapositiva usando el Word como referencia, o trasladar el esquema validado a una plantilla manualmente. La función puede variar por licencia y configuración.

## Repositorios

- Las fuentes reutilizables están en `template/`.
- La secuencia docente, los prompts literales y los resultados esperados están en `delivery/`.

## Referencias de producto

- [Crear una presentación con Copilot en PowerPoint — Soporte de Microsoft](https://support.microsoft.com/es-es/office/crear-una-presentaci%C3%B3n-con-copilot-en-powerpoint)
- [Preguntas más frecuentes sobre Copilot en PowerPoint — Soporte de Microsoft](https://support.microsoft.com/es-es/office/preguntas-m%C3%A1s-frecuentes-sobre-copilot-en-powerpoint)
