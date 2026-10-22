"""Demo web para explorar tareas de análisis de texto con Azure AI Language."""
import os

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask(__name__)

MAX_TEXT_LENGTH = 5000


def create_client():
    endpoint = os.getenv("LANGUAGE_ENDPOINT", "").strip()
    key = os.getenv("LANGUAGE_KEY", "").strip()
    if not endpoint or endpoint.startswith("PON_AQUI"):
        raise ValueError("Configura LANGUAGE_ENDPOINT en el archivo .env.")
    if not key or key.startswith("PON_AQUI"):
        raise ValueError("Configura LANGUAGE_KEY en el archivo .env.")
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    task = str(payload.get("task", "")).strip()

    if not text:
        return jsonify({"error": "Escribe o pega un texto para analizar."}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"El texto supera el límite de {MAX_TEXT_LENGTH} caracteres."}), 400

    try:
        client = create_client()
        document = {"id": "1", "text": text, "country_hint": "BO"}

        if task == "language":
            result = client.detect_language([document], country_hint="BO")[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            lang = result.primary_language
            data = {
                "title": "Idioma detectado",
                "summary": f"Azure Language identificó el idioma principal del texto.",
                "items": [
                    {"label": "Idioma", "value": lang.name},
                    {"label": "Código ISO 639-1", "value": lang.iso6391_name},
                    {"label": "Confianza", "value": f"{lang.confidence_score:.1%}"},
                ],
            }
        elif task == "key_phrases":
            result = client.extract_key_phrases([document])[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            data = {"title": "Frases clave", "items": [{"label": "Frase", "value": p} for p in result.key_phrases]}
            if not result.key_phrases:
                data["summary"] = "No se encontraron frases clave en el texto."
        elif task == "entities":
            result = client.recognize_entities([document])[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            data = {
                "title": "Entidades reconocidas",
                "items": [
                    {"label": entity.category, "value": entity.text, "detail": f"Confianza: {entity.confidence_score:.1%}"}
                    for entity in result.entities
                ],
            }
            if not result.entities:
                data["summary"] = "No se encontraron entidades reconocibles."
        elif task == "sentiment":
            result = client.analyze_sentiment([document], show_opinion_mining=True)[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            data = {
                "title": "Análisis de sentimiento",
                "items": [
                    {"label": "Sentimiento general", "value": result.sentiment.capitalize()},
                    {"label": "Positivo", "value": f"{result.confidence_scores.positive:.1%}"},
                    {"label": "Neutral", "value": f"{result.confidence_scores.neutral:.1%}"},
                    {"label": "Negativo", "value": f"{result.confidence_scores.negative:.1%}"},
                ],
            }
        elif task == "pii":
            result = client.recognize_pii_entities([document], language="es")[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            data = {
                "title": "Información personal detectada",
                "items": [
                    {"label": entity.category, "value": entity.text, "detail": f"Confianza: {entity.confidence_score:.1%}"}
                    for entity in result.entities
                ],
                "redacted_text": result.redacted_text,
            }
            if not result.entities:
                data["summary"] = "No se identificó información personal reconocible."
        elif task == "summary":
            # Usamos extracción de frases para ofrecer una versión introductoria,
            # compatible con el recurso Azure Language usado en este laboratorio.
            result = client.extract_key_phrases([document])[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            phrases = result.key_phrases
            data = {
                "title": "Resumen introductorio",
                "summary": " · ".join(phrases[:5]) if phrases else "No fue posible extraer ideas principales del texto.",
                "items": [{"label": "Idea clave", "value": phrase} for phrase in phrases],
                "note": "Esta opción muestra frases clave como resumen didáctico; no es el servicio dedicado de resumen generativo.",
            }
        else:
            return jsonify({"error": "Selecciona una tarea válida."}), 400

        return jsonify(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 500
    except AzureError as error:
        message = getattr(error, "message", None) or str(error)
        return jsonify({"error": f"Azure AI Language: {message}"}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
