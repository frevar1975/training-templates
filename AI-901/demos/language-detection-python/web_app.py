"""Aplicación web local para análisis de texto con Azure AI Language."""
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
    operation = str(payload.get("operation", "language")).strip().lower()

    if not text:
        return jsonify({"error": "Escribe un texto para analizar."}), 400
    if len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": f"El texto no puede superar {MAX_TEXT_LENGTH} caracteres."}), 400
    if operation not in {"language", "entities"}:
        return jsonify({"error": "Selecciona un tipo de análisis válido."}), 400

    try:
        client = create_client()
        if operation == "language":
            result = client.detect_language(
                documents=[{"id": "1", "text": text, "country_hint": "BO"}],
                country_hint="BO",
            )[0]
            if result.is_error:
                return jsonify({"error": result.error.message}), 400
            language = result.primary_language
            return jsonify({
                "operation": "language",
                "language": language.name,
                "iso": language.iso6391_name,
                "confidence": round(language.confidence_score * 100, 2),
            })

        result = client.recognize_entities(
            documents=[{"id": "1", "text": text}],
            language="en",
        )[0]
        if result.is_error:
            return jsonify({"error": result.error.message}), 400
        return jsonify({
            "operation": "entities",
            "entities": [
                {
                    "text": entity.text,
                    "category": entity.category,
                    "subcategory": entity.subcategory,
                    "confidence": round(entity.confidence_score * 100, 2),
                }
                for entity in result.entities
            ],
        })
    except ValueError as error:
        return jsonify({"error": str(error)}), 500
    except AzureError as error:
        return jsonify({"error": f"Azure AI Language: {error.message}"}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
