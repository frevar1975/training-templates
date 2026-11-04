"""Interfaz web local para la demostración AI-3016 Día 3."""
import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))
from common import get_client

DOC = ROOT / "demo-data" / "politica_viajes_demo.txt"
app = Flask(__name__)
client, deployment = get_client()
vector_store_id = None

FUNCTION_TOOL = {
    "type": "function", "name": "consultar_disponibilidad",
    "description": "Consulta disponibilidad ficticia de una visita guiada. No reserva.",
    "parameters": {
        "type": "object",
        "properties": {
            "fecha": {"type": "string", "description": "Fecha AAAA-MM-DD"},
            "hora": {"type": "string", "description": "Hora HH:MM"},
            "personas": {"type": "integer", "description": "Cantidad de personas"},
        },
        "required": ["fecha", "hora", "personas"], "additionalProperties": False,
    },
}


def sources_from(response):
    sources = []
    for item in response.output:
        if item.type != "message":
            continue
        for content in item.content:
            for annotation in getattr(content, "annotations", []) or []:
                if getattr(annotation, "type", "") == "url_citation":
                    url = getattr(annotation, "url", "")
                    if url and url not in [s["url"] for s in sources]:
                        sources.append({"title": getattr(annotation, "title", "Fuente"), "url": url})
    return sources


def ensure_vector_store():
    global vector_store_id
    if vector_store_id is None:
        store = client.vector_stores.create(name="AI-3016-Dia-3-Politica-Web-Demo")
        vector_store_id = store.id
        with DOC.open("rb") as f:
            client.vector_stores.files.upload_and_poll(vector_store_id=vector_store_id, file=f)
    return vector_store_id


def run_function(prompt):
    instructions = (
        "Responde en español. Si piden disponibilidad, usa consultar_disponibilidad. "
        "No afirmes que reservaste. Aclara que los datos son ficticios."
    )
    first = client.responses.create(model=deployment, instructions=instructions,
                                    input=prompt, tools=[FUNCTION_TOOL])
    outputs = []
    trace = []
    for item in first.output:
        if item.type == "function_call" and item.name == "consultar_disponibilidad":
            args = json.loads(item.arguments)
            trace.append({"step": "El modelo solicitó la función", "data": args})
            result = {"fecha_solicitada": args["fecha"], "hora_solicitada": args["hora"],
                      "personas_solicitadas": args["personas"], "hay_disponibilidad": True,
                      "lugares_disponibles_demo": 6,
                      "nota": "Dato ficticio; no se hizo ninguna reserva."}
            trace.append({"step": "La aplicación ejecutó la función simulada", "data": result})
            outputs.append({"type": "function_call_output", "call_id": item.call_id,
                            "output": json.dumps(result, ensure_ascii=False)})
    if not outputs:
        return first.output_text, trace, []
    final = client.responses.create(model=deployment, previous_response_id=first.id,
                                    input=outputs, tools=[FUNCTION_TOOL], instructions=instructions)
    return final.output_text, trace, []


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/demo")
def demo():
    body = request.get_json(silent=True) or {}
    tool = body.get("tool", "")
    prompt = (body.get("prompt") or "").strip()
    if tool not in {"code_interpreter", "web_search", "file_search", "function_calling"}:
        return jsonify(error="Elige una herramienta válida."), 400
    if not prompt:
        return jsonify(error="Escribe una consulta."), 400
    try:
        trace, sources = [], []
        if tool == "code_interpreter":
            response = client.responses.create(model=deployment, input=prompt,
                tools=[{"type": "code_interpreter", "container": {"type": "auto"}}])
            text = response.output_text
            trace = [{"step": "Code Interpreter invocado", "data": any(
                x.type == "code_interpreter_call" for x in response.output)}]
        elif tool == "web_search":
            response = client.responses.create(model=deployment, input=prompt,
                tools=[{"type": "web_search"}])
            text, sources = response.output_text, sources_from(response)
        elif tool == "file_search":
            store_id = ensure_vector_store()
            response = client.responses.create(model=deployment, input=prompt, tools=[{
                "type": "file_search", "vector_store_ids": [store_id]}])
            text = response.output_text
            trace = [{"step": "Documento de política de viajes consultado", "data": "demo-data/politica_viajes_demo.txt"}]
        else:
            text, trace, sources = run_function(prompt)
        return jsonify(answer=text, sources=sources, trace=trace)
    except Exception as exc:
        app.logger.exception("Error en demo")
        return jsonify(error=str(exc)), 500


if __name__ == "__main__":
    # Solo escucha en localhost; no expone credenciales ni el servidor a la red.
    app.run(host="127.0.0.1", port=int(os.getenv("WEB_DEMO_PORT", "5000")), debug=False)
