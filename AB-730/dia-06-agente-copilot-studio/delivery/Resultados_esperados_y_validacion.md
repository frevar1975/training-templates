# Resultados esperados y validación del agente

Usa esta hoja para verificar las pruebas en Copilot Studio. El agente puede variar la redacción; evalúa exactitud, respaldo y matices.

## Demo 1 — Proyecto Atlas

Debe identificar que la integración de notificaciones está conectada, que Priya valida reintentos con objetivo 6 de noviembre de 2026 y que Luis sigue con el flujo de aprobación, cuya prueba con cliente tiene objetivo 9 de noviembre. La prueba depende del acceso de Marina López; soporte no indicó fecha. El rastreador conserva 70%; cerca de 80% es una opinión no validada. Camden revisará tareas duplicadas el 5 de noviembre. La revisión del 13 de noviembre es una previsión interna por confirmar con el cliente.

**Fallo crítico:** comunicar 80% como cifra oficial, 13 de noviembre como fecha confirmada, o acceso como ya habilitado.

## Demo 2 — Zapatería Paso Firme

Debe informar nueve pedidos confirmados (PF-1001 a PF-1009), un cambio de talla PF-1004 que no cuenta como venta adicional, y dos pares Urbano 24 talla 39 disponibles al cierre. Una consulta por esa talla se convirtió en PF-1008; la otra persona compró en otro lugar. Todos los pedidos aparecen pagados y entregados o retirados. No hay precios, por lo que no se pueden calcular ingresos ni márgenes.

**Fallo crítico:** contar PF-1004 como décima venta, inventar precio/ingreso o afirmar una tasa de conversión general.

## Demo 3 — Proyecto Nébula

| Semana | Planificadas | Completadas | Tasa |
|---|---:|---:|---:|
| 28 sep–4 oct | 10 | 8 | 80% |
| 5–11 oct | 10 | 9 | 90% |
| 12–18 oct | 10 | 9 | 90% |
| 19–25 oct | 10 | 5 | 50% |
| 26 oct–1 nov | 10 | 8 | 80% |

Total: 39 de 50 tareas (78%). La caída entre 12–18 y 19–25 de octubre es de 40 puntos porcentuales; luego hay recuperación de 30 puntos. Durante la semana de 50%, tres tareas quedaron en curso y dos bloqueadas. El archivo no prueba una causa única.

**Fallo crítico:** llamar “40%” a la diferencia sin aclarar puntos porcentuales, o atribuir la caída exclusivamente a un bloqueo.

## Lista de comprobación

- [ ] Respondió con el ejemplo solicitado.
- [ ] No mezcló información de otros archivos.
- [ ] Los hechos importantes coinciden con la fuente.
- [ ] Identificó incertidumbres y datos ausentes.
- [ ] No prometió conectar aplicaciones ni modificar archivos.
- [ ] La cita o referencia de conocimiento aparece si la interfaz la ofrece.
