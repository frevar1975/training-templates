\# Delivery Día 6 — Informe de estado semanal



\*\*Curso:\*\* AB-730T00  

\*\*Módulo:\*\* 6 — Definir el rol de Copilot en los flujos de trabajo  

\*\*Herramienta:\*\* Copilot Chat  

\*\*Duración:\*\* 30 minutos  

\*\*Escenario:\*\* informe semanal del proyecto Atlas



\## Preparación realizada



Se cargaron los cuatro archivos de `template/` en una carpeta de SharePoint y se agregó esa carpeta a Copilot Chat como fuente. Como Copilot admite hasta tres archivos adjuntos por mensaje, usar la carpeta de SharePoint permitió consultar las cuatro fuentes juntas.



\## Flujo de la demostración



1\. Pedir a Copilot una tabla preliminar con hechos, responsables, plazos y fuentes, sin redactar todavía el informe.

2\. Revisar la discrepancia entre el 70% registrado y la estimación informal cercana al 80%.

3\. Generar el informe semanal a partir de las fuentes.

4\. Revisar y corregir expresiones que exageraban el estado de las notificaciones o la importancia del bloqueo.

5\. Confirmar que el informe mantuviera la fecha del 13 de noviembre como previsión interna pendiente de confirmación con el cliente.



\## Prompts utilizados



\### Consolidar las fuentes



> Usa los cuatro archivos de la carpeta de SharePoint que agregué a este chat. Todavía no redactes el informe. Primero crea una tabla con tema, actualización, estado, responsable, fecha o plazo y archivo de origen. Si un dato no aparece, escribe “No especificado”. Separa hechos de interpretaciones e identifica contradicciones entre las fuentes.



\### Redactar el informe



> Con base en la tabla consolidada y en los cuatro archivos, redacta el informe de estado semanal del proyecto Atlas para el responsable del equipo. Incluye resumen ejecutivo, avances, próximos pasos, riesgos o bloqueos y decisiones requeridas. Presenta el 70% como el dato del rastreador y aclara que el 80% es una estimación no validada. Indica que el acceso de Marina sigue pendiente y que la fecha del 13 de noviembre es una previsión interna que se debe confirmar con el cliente. No inventes datos ni responsables.



\### Revisar el lenguaje



> Revisa el informe sin cambiar su estructura. Aclara que la conexión de notificaciones está hecha, pero las pruebas de reintento siguen pendientes. Describe el acceso como una dependencia pendiente que condiciona la prueba de aprobación. Conserva cifras, fechas, responsables y advertencias respaldadas por los archivos. No agregues información nueva.



\## Aprendizajes observados



\- Copilot organizó información de distintas fuentes y mostró de dónde provenían los datos.

\- La revisión humana permitió distinguir el 70% del rastreador de la estimación no validada.

\- La fecha del 13 de noviembre quedó identificada como previsión interna, no como confirmación del cliente.

\- La conexión de notificaciones está realizada, pero la validación de reintentos continúa pendiente.

\- El acceso de Marina condiciona la prueba de aprobación y todavía no tiene fecha de resolución.



\## Resultado



Se obtuvo un borrador de informe semanal con avances, próximos pasos, riesgos y decisiones requeridas. El usuario revisó el contenido y pidió ajustes para que las afirmaciones reflejaran con precisión las fuentes.

