"""Demo 3: el modelo recupera información de un documento cargado."""
import argparse
import os

from common import get_client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keep-store",
        action="store_true",
        help="Conserva el vector store para inspeccionarlo en Foundry.",
    )
    args = parser.parse_args()

    client, deployment = get_client()
    document_path = os.path.join(
        os.path.dirname(__file__), "demo-data", "politica_viajes_demo.txt"
    )
    vector_store = None

    try:
        vector_store = client.vector_stores.create(
            name="AI-3016-Dia-3-Politica-Demo"
        )
        with open(document_path, "rb") as document:
            client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=document,
            )

        question = (
            "Según la política, ¿con cuánta anticipación se reserva el viaje, "
            "cuál es el límite diario de comida y qué dice sobre extender la estadía? "
            "Separa lo que está indicado de lo que no aparece en el documento."
        )
        response = client.responses.create(
            model=deployment,
            input=question,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store.id],
                }
            ],
        )
        print("\n=== RESPUESTA BASADA EN EL ARCHIVO ===\n")
        print(response.output_text)
        print(f"\nVector store creado: {vector_store.id}")
    finally:
        if vector_store and not args.keep_store:
            client.vector_stores.delete(vector_store.id)
            print("Vector store temporal eliminado.")


if __name__ == "__main__":
    main()
