# Demo de interacción con un agente de Foundry

Demo mínimo: una página de chat que envía mensajes a un agente de Microsoft Foundry y muestra sus respuestas.

## Preparar

1. Crea un entorno virtual e instala dependencias:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copia `.env.example` como `.env` y completa:
   - `FOUNDRY_PROJECT_ENDPOINT`: endpoint del proyecto de Foundry.
   - `FOUNDRY_AGENT_NAME`: nombre exacto del agente.

3. Inicia sesión para que `DefaultAzureCredential` pueda autenticar el demo:

   ```powershell
   az login
   ```

## Ejecutar

```powershell
python app.py
```

Abre `http://127.0.0.1:5000`.

El demo no expone credenciales en el navegador. La llamada a Foundry ocurre en el endpoint Flask `/api/chat`.
