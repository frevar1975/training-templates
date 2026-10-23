# AI-901T00-A — Introducción a la IA en Azure

Plantilla reutilizable para preparar y dictar el curso **Introduction to AI in Azure**.

> Esta carpeta contiene contenido base por código de curso. No incluir aquí fechas, centro de capacitación, alumnos, credenciales ni datos de una edición concreta. Las ejecuciones se documentan en `training-delivery`.

## Datos del curso

- **Código:** AI-901T00-A
- **Nivel:** Principiante
- **Producto:** Azure / Microsoft Foundry
- **Audiencia:** profesionales de tecnología que comienzan a desarrollar soluciones de IA
- **Duración publicada por Microsoft Learn:** 1 día
- **Requisitos recomendados:** fundamentos de computación y matemática; conocimientos básicos de Python y conceptos de nube son útiles para los ejercicios técnicos.

La duración y distribución de una entrega pueden variar según el centro. Registrar el calendario real fuera de esta plantilla.

## Objetivo

Presentar conceptos fundamentales de inteligencia artificial y los servicios de Azure que permiten crear soluciones de IA. El curso combina conceptos y experiencias prácticas introductorias.

## Rutas oficiales relacionadas

1. [AI concepts for developers and technology professionals](https://learn.microsoft.com/en-us/training/paths/ai-concepts/) — conceptos y terminología de IA; aborda IA generativa y agentes, visión por computadora, voz, NLP y análisis de texto, extracción de información y RAG.
2. [Get started with AI applications and agents on Azure](https://learn.microsoft.com/en-us/training/paths/get-started-with-artificial-intelligence-on-azure/) — introducción a cargas de trabajo de IA en Microsoft Foundry y práctica con IA generativa y agentes, análisis de texto, voz, visión por computadora, extracción de información y Foundry IQ.

[Descripción oficial del curso AI-901T00-A](https://learn.microsoft.com/en-us/training/courses/ai-901t00)

## Contenido de este template

- [Guía del instructor](trainer-guide.md)
- [Mapa temático y sugerencia de agrupación](module-map.md)
- [Plantilla reutilizable de sesión](session-template.md)
- [Demo: cargar audio y transcribir con Azure Speech](demos/speech-audio-upload/README.md)

## Enfoque de enseñanza

Para cada tema, preparar tres piezas breves:

1. **Concepto:** qué es y qué problema resuelve.
2. **Analogía:** una comparación cotidiana que aclare el concepto.
3. **Ejemplo real:** un caso de uso reconocible.

Cuando el tema lo permita, complementar con una demostración o actividad práctica. Explicar siempre qué resultado debe observar el alumno y qué limitaciones o consideraciones de uso debe tener presentes.

## Estructura sugerida para extender el repositorio

```text
AI-901/
├── README.md
├── trainer-guide.md
├── module-map.md
├── session-template.md
├── demos/
├── labs/
├── prompts/
├── scripts/
└── datasets/
```

Crear subcarpetas solo cuando exista material reutilizable para compartir. No guardar información sensible ni datos personales en este repositorio.
