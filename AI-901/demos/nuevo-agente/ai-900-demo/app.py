import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

app = Flask(__name__)


def get_agent_response(message: str) -> str:
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    agent_name = os.getenv("FOUNDRY_AGENT_NAME")

    if not endpoint or not agent_name:
        raise RuntimeError(
            "Configura FOUNDRY_PROJECT_ENDPOINT y FOUNDRY_AGENT_NAME en el archivo .env"
        )

    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    response = openai.responses.create(
        input=message,
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "type": "agent_reference",
            }
        },
    )

    return response.output_text


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Escribe un mensaje."}), 400

    try:
        reply = get_agent_response(message)
        return jsonify({"reply": reply})
    except Exception as error:
        app.logger.exception("Error al consultar el agente de Foundry")
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True)