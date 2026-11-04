# Día 6 — Informe de estado semanal

Demo del módulo 6 de AB-730T00. El ejercicio muestra cómo usar Copilot Chat para reunir información de varias fuentes, identificar discrepancias y preparar un informe semanal verificable.

## Estructura

- `template/`: fuentes ficticias reutilizables para el ejercicio.
- `delivery/`: guía del instructor, prompts y resultados esperados.

## Escenario

Camden prepara el informe semanal del Proyecto Atlas con un correo, un chat del equipo, un rastreador de tareas y notas de reunión.

## Objetivos

- Consolidar la información e identificar su fuente.
- Distinguir hechos explícitos de interpretaciones.
- Detectar datos que requieren confirmación.
- Redactar y revisar un informe para una audiencia definida.

## Ejecución en Copilot Chat

1. Carga las cuatro fuentes de `template/` en una ubicación de SharePoint accesible para Copilot.
2. Pide que consolide los datos sin redactar todavía el informe.
3. Revisa las discrepancias de avance, fecha y acceso.
4. Genera el informe semanal con un prompt que prohíba inventar datos.
5. Revisa y corrige afirmaciones que excedan lo que dicen las fuentes.

Consulta `delivery/` para la guía del instructor y los prompts utilizados.

## Extensión con un agente

Para configurar en Copilot Studio un agente Standard que atienda los tres demos de forma independiente, consulta el [paquete del agente](../dia-06-agente-copilot-studio/README.md).
