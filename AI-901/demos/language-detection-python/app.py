"""Demo de análisis de texto con Azure AI Language."""
import os
import sys

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from dotenv import load_dotenv


def create_client():
    load_dotenv()
    endpoint = os.getenv("LANGUAGE_ENDPOINT", "").strip()
    key = os.getenv("LANGUAGE_KEY", "").strip()

    if not endpoint or endpoint.startswith("PON_AQUI"):
        raise ValueError("Completa LANGUAGE_ENDPOINT en el archivo .env.")
    if not key or key.startswith("PON_AQUI"):
        raise ValueError("Completa LANGUAGE_KEY en el archivo .env.")

    return TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


def analyze_texts(client, texts):
    documents = [
        {"id": str(i), "text": text, "country_hint": "BO"}
        for i, text in enumerate(texts, start=1)
    ]
    results = client.detect_language(documents=documents, country_hint="BO")

    for result in results:
        print("-" * 68)
        if result.is_error:
            print(f"Documento {result.id}: error {result.error.code}")
            print(result.error.message)
            continue

        language = result.primary_language
        print(f"Texto: {result.id}")
        print(f"Idioma: {language.name}")
        print(f"Código ISO 639-1: {language.iso6391_name}")
        print(f"Confianza: {language.confidence_score:.0%}")


def main():
    sample_texts = [
        (
            "Un cliente escribe para consultar por la instalación de internet "
            "en su domicilio. Quiere conocer los planes disponibles, el precio "
            "mensual y el tiempo aproximado de instalación en Santa Cruz."
        ),
        (
            "The customer wants to know which internet plans are available "
            "and how long the installation will take."
        ),
        (
            "La atención fue rápida y el técnico explicó claramente cómo "
            "configurar el router."
        ),
    ]

    try:
        client = create_client()
        analyze_texts(client, sample_texts)
        return 0
    except ValueError as error:
        print(f"Configuración: {error}", file=sys.stderr)
        return 1
    except AzureError as error:
        print(f"Error de Azure Language: {error.message}", file=sys.stderr)
        print(
            "Verifica que el endpoint y la clave pertenezcan al mismo recurso.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
