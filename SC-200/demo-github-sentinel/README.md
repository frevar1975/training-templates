# Demo: desplegar una consulta de Microsoft Sentinel desde GitHub

## Propósito

Mostrar cómo una consulta de búsqueda se administra como contenido versionado: se crea el archivo en el repositorio, GitHub Actions lo despliega y Microsoft Sentinel lo muestra en el workspace.

La KQL de esta demostración usa `print` para devolver una fila de prueba. No requiere conectores ni eventos ingeridos y no genera alertas.

## Datos que completar para cada ejecución

- **Curso:** [código del curso]
- **Centro y periodo:** [centro-periodo]
- **Repositorio de contenido:** [owner/repo]
- **Rama de despliegue:** [rama]
- **Workspace Sentinel:** [workspace]
- **Workflow:** [nombre del workflow]
- **Título de la consulta:** [título único]

No incluir contraseñas, tokens ni secretos en este documento.

## Preparación

1. Confirmar que Microsoft Sentinel está habilitado en el workspace y que el workspace está conectado al repositorio indicado.
2. Confirmar que el workflow de despliegue está habilitado y que su identidad conserva los permisos necesarios.
3. Abrir el repositorio y comprobar que existe la carpeta de contenido de consultas. Registrar el nombre del workflow y la rama exactos.

## Demo paso a paso

### 1. Crear el contenido en GitHub

1. En el repositorio de contenido, abrir la carpeta configurada para consultas.
2. Seleccionar **Add file → Create new file**.
3. Crear un archivo JSON con nombre único, por ejemplo `[prefijo]-Demo-RepoQuery-1.json`.
4. Completar el nombre interno y el título visibles. Usar como base este ARM template:

~~~json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "workspace": {
      "type": "string"
    }
  },
  "resources": [
    {
      "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
      "apiVersion": "2020-03-01-preview",
      "name": "[concat(parameters('workspace'), '/[nombre-interno-unico]')]",
      "properties": {
        "Category": "Hunting Queries",
        "DisplayName": "[título visible de la consulta]",
        "Query": "print Demo = 'Consulta creada en GitHub y desplegada en Sentinel'",
        "Tags": [
          {
            "Name": "Description",
            "Value": "Consulta de demostración de despliegue desde GitHub."
          },
          {
            "Name": "Tactics",
            "Value": "Discovery"
          }
        ]
      }
    }
  ]
}
~~~

5. Hacer commit directamente en la rama de despliegue configurada. El workflow debe estar suscrito a cambios de esa rama y a la ruta del archivo.

### 2. Verificar GitHub Actions

1. Abrir **Actions** en el repositorio.
2. Abrir el run asociado al commit.
3. Esperar a que el run finalice correctamente.
4. Revisar el job de despliegue y confirmar que el paso de publicación de contenido a Microsoft Sentinel terminó sin error.

Si no se inicia un run, verificar rama, rutas configuradas en el trigger del workflow y estado de Actions.

### 3. Confirmar el contenido en Sentinel

1. Abrir el workspace correcto en Microsoft Sentinel.
2. Ir a **Threat management → Hunting → Queries** (puede aparecer como **Consultas**).
3. Buscar el título visible de la consulta.
4. Confirmar que el origen del contenido indica **Repositories/Repositorios**.

Las consultas guardadas aparecen en **Queries/Consultas**. No confundirlas con **Hunts/Búsquedas**, que son investigaciones distintas.

### 4. Ejecutar la KQL de prueba

1. Abrir **Advanced hunting / Búsqueda avanzada** en el workspace correcto.
2. Pegar la consulta:

~~~kusto
print Demo = 'Consulta creada en GitHub y desplegada en Sentinel'
~~~

3. Seleccionar **Run query / Ejecutar consulta**.
4. Mostrar que el resultado contiene una fila con la columna `Demo`.

La lista de consultas comprueba el despliegue del contenido. Advanced hunting comprueba que la KQL se ejecuta. Si el editor está vacío, pegar la KQL manualmente: son pantallas distintas.

## Guion oral

> “Definimos la consulta como contenido versionado en GitHub. El commit inicia el workflow, que publica el archivo en el workspace de Sentinel. Verificamos el run en Actions, encontramos la consulta con origen Repositories y ejecutamos una KQL simple para comprobar el resultado.”

## Criterios de éxito

- El commit está en la rama configurada.
- GitHub Actions finaliza correctamente.
- La consulta aparece en el workspace correcto con origen Repositories.
- La KQL de prueba devuelve una fila.

## Notas para adaptar la plantilla

- Usar nombres internos únicos para evitar conflictos o sobrescribir otra consulta.
- Confirmar el filtro de rutas y la rama del workflow antes de presentar.
- Esta demo enseña administración y despliegue de contenido; no simula una detección ni genera una alerta.
