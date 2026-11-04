# Demo 1 — Informe de estado semanal

**Curso:** AB-730T00 · **Día:** 6 · **Herramienta:** Copilot Chat · **Duración:** 30 minutos

Guion del instructor para mostrar cómo Copilot reúne fuentes de SharePoint, organiza los datos, redacta un informe y revisa afirmaciones que necesitan confirmación. Los datos del Proyecto Atlas son ficticios. El demo de Copilot Studio se hará por separado para crear un agente reutilizable.

## Preparación

1. Abre Copilot Chat con la cuenta que usarás en clase.
2. Confirma que la carpeta de SharePoint contiene los cuatro archivos de `template/`: correo, chat, rastreador y notas de reunión.
3. Agrega esa carpeta como fuente del chat y comprueba que Copilot puede encontrar los archivos.
4. La interfaz puede limitar los adjuntos a tres por mensaje. Usa la carpeta de SharePoint como fuente. Si no funciona, adjunta correo, chat y rastreador; después agrega las notas en otro mensaje del mismo chat y pídele que actualice la tabla.

## Guion de 30 minutos

| Tiempo | Acción | Qué decir |
|---|---|---|
| 0–3 min | Presenta el reto de Camden. Muestra Copilot Chat y la carpeta. | “Camden tiene que entregar el informe semanal en poco tiempo. La información está repartida entre correo, chat, rastreador y notas de reunión. Vamos a pedirle a Copilot que la reúna y luego revisaremos si lo que redacta está respaldado.” |
| 3–8 min | Envía el Prompt 1. Revisa cobertura y fuentes. | “Primero estamos creando un inventario con fuentes. Así reducimos el riesgo de mezclar hechos con suposiciones.” |
| 8–15 min | Envía el Prompt 2. Revisa resumen, avances, bloqueos y decisiones. | “Fíjense en cómo delimitamos audiencia y estructura, y especificamos qué hacer con datos inciertos. Un prompt claro no elimina la revisión; nos ayuda a saber qué revisar.” |
| 15–22 min | Envía el Prompt 3. Pregunta al grupo por las discrepancias. | “¿El 80% aparece en el rastreador? ¿Quién confirmó el 13 de noviembre con el cliente? ¿Soporte dio una fecha para habilitar el acceso?” |
| 22–27 min | Envía el Prompt 4 para corregir precisión. Si queda tiempo, usa el Prompt 5. | “Vamos a pedir precisión sin rehacer todo el informe ni introducir datos nuevos.” |
| 27–30 min | Cierra con preguntas de reflexión. | “En Copilot Chat resolvimos una tarea puntual. En Copilot Studio crearemos un agente que siga instrucciones definidas para repetir este proceso.” |

## Prompts exactos

### Prompt 1 — Consolidar las fuentes

> Usa los cuatro archivos de la carpeta de SharePoint que agregué a este chat. Todavía no redactes el informe. Primero crea una tabla con tema, actualización, estado, responsable, fecha o plazo y archivo de origen. Si un dato no aparece, escribe “No especificado”. Separa hechos de interpretaciones e identifica contradicciones entre las fuentes.

**Revisa que aparezcan:** la conexión de notificaciones, las pruebas de reintento pendientes, el 70% del rastreador, la estimación no validada cercana al 80%, el acceso pendiente de Marina y la fecha interna prevista para la revisión.

### Prompt 2 — Redactar el informe

> Con base en la tabla consolidada y en los cuatro archivos, redacta el informe de estado semanal del proyecto Atlas para el responsable del equipo. Incluye resumen ejecutivo, avances, próximos pasos, riesgos o bloqueos y decisiones requeridas. Presenta el 70% como el dato del rastreador y aclara que el 80% es una estimación no validada. Indica que el acceso de Marina sigue pendiente y que la fecha del 13 de noviembre es una previsión interna que se debe confirmar con el cliente. No inventes datos ni responsables.

**Revisa:** responsables y fechas contra el rastreador. No aceptes un dato solo porque Copilot lo presenta con seguridad.

### Prompt 3 — Verificar afirmaciones

> Revisa cada afirmación del informe y crea una tabla con afirmación, archivo que la respalda y dato de origen. Marca “Sin respaldo” cuando no puedas verificarla. Comprueba especialmente el porcentaje de avance, la fecha de revisión con el cliente y el estado del acceso de Marina.

**Respuesta esperada:** el rastreador marca 70%; Luis estima cerca de 80%, pero no actualizó el rastreador. El 13 de noviembre figura en planificación interna y debe confirmarse con el cliente. Soporte no indicó fecha para el acceso.

### Prompt 4 — Ajustar precisión

> Revisa el informe sin cambiar su estructura. Aclara que la conexión de notificaciones está hecha, pero las pruebas de reintento siguen pendientes. Describe el acceso como una dependencia pendiente que condiciona la prueba de aprobación. Conserva las cifras, fechas, responsables y advertencias respaldadas por los archivos. No agregues información nueva.

### Prompt 5 — Adaptar al director (opcional)

> Reduce el resumen ejecutivo a un máximo de 150 palabras para el director del proyecto. Conserva los riesgos, las decisiones requeridas y los datos pendientes de confirmar. No conviertas la previsión interna del 13 de noviembre en una fecha confirmada por el cliente.

## Resultado que debe quedar claro

- El rastreador registra 70%; el 80% es una estimación no validada.
- La conexión de notificaciones está realizada; faltan pruebas de reintento.
- El flujo de aprobación continúa en curso y su prueba depende del acceso de Marina.
- Soporte todavía no comunicó una fecha para habilitar el acceso.
- El 13 de noviembre es una previsión interna pendiente de confirmación con el cliente.
- No se deben inventar fechas, responsables, causas ni aprobaciones.

## Si Copilot no encuentra los archivos

Di: “Revisemos que la carpeta esté agregada como fuente y que tengamos permisos”. Si solo permite tres adjuntos, carga correo, chat y rastreador; luego añade las notas en un mensaje posterior del mismo chat y pide actualizar la tabla. También puedes pegar las fuentes por separado. Usa datos ficticios y una ubicación autorizada.
