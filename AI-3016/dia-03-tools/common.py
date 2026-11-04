"""Configuración compartida por los demos AI-3016 de Día 3."""
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI


def get_client():
    load_dotenv()
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "").strip().rstrip("/")
    deployment = os.getenv("MODEL_DEPLOYMENT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()

    if not endpoint or not deployment:
        raise RuntimeError(
            "Completa FOUNDRY_PROJECT_ENDPOINT y MODEL_DEPLOYMENT en el archivo .env."
        )

    if api_key:
        credential = api_key
    else:
        # Inicio de sesión previo: az login
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default",
        )
        credential = token_provider()

    client = OpenAI(
        base_url=f"{endpoint}/openai/v1/",
        api_key=credential,
    )
    return client, deployment
