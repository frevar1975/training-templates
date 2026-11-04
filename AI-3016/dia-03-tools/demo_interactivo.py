"""Menú interactivo AI-3016: selecciona una herramienta y escribe tu consulta."""
import argparse
import json
import os

from common import get_client

TOOLS = {
    "1": "Code Interpreter",
    "2": "Web Search",
    "3": "File Search",
    "4": "Function calling",
}

FUNCTION_TOOL = {
    "type": "function",
    "name": "consultar_disponibilidad",
    "description": (
        "Consulta disponibilidad ficticia de una visita guiada en Buenos Aires. "
        "No reserva ni confirma lugares."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "fecha": {"type": "string", "description": "Fecha AAAA-MM-DD."},
            "hora": {"type": "string", "description": "Hora HH:MM."},
            "personas": {"type": "integer", "description": "Cantidad de personas."},
        },
        "required": ["fecha", "hora", "personas"],
        "additionalProperties": False,
    },
}


def print_sources(response):
    sources = []
    for item in response.output:
        if item.type != "message":
            continue
        for content in item.content:
            for annotation in getattr(content, "annotations", []) or []:
                if getattr(annotation, "type", "") == "url_citation":
                    title = getattr(annotation, "title", "Fuente")
                    url = getattr(annotation, "url", "")
                    if url and (title, url) not in sources:
                        sources.append((title, url))
    if sources:
        print("\nFuentes:")
        for title, url in sources:
            print(f"- {title}: {url}")


def call_local_function(arguments):
    # Simula un sistema de disponibilidad. No consulta datos reales ni reserva.
    return {
        "fecha_solicitada": arguments["fecha"],
        "hora_solicitada": arguments["hora"],
        "personas_solicitadas": arguments["personas"],
        "hay_disponibilidad": True,
        "lugares_disponibles_demo": 6,
        "nota": "Dato ficticio de clase; no se hizo ninguna reserva.",
    }


def run_function_calling(client, deployment, prompt):
    instructions = (
        "Responde en español. Si la consulta pide disponibilidad de la visita guiada, "
        "usa consultar_disponibilidad. No afirmes que se realizó una reserva. "
        "Aclara que los datos devueltos son ficticios."
    )
    response = client.responses.create(
        model=deployment,
        instructions=instructions,
        input=prompt,
        tools=[FUNCTION_TOOL],
    )
    outputs = []
    for item in response.output:
        if item.type == "function_call" and item.name == "consultar_disponibilidad":
            arguments = json.loads(item.arguments)
            print("\n[El modelo pidió ejecutar la función]")
            print(json.dumps(arguments, ensure_ascii=False, indent=2))
            result = call_local_function(arguments)
            print("\n[La aplicación ejecutó la función local simulada]")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

    if not outputs:
        print("\nEl modelo respondió sin pedir la función:")
        print(response.output_text)
        return

    final = client.responses.create(
        model=deployment,
        previous_response_id=response.id,
        input=outputs,
        tools=[FUNCTION_TOOL],
        instructions=instructions,
    )
    print("\nRespuesta final:")
    print(final.output_text)


def main():
    parser = argparse.ArgumentParser(description="Demo interactiva de herramientas.")
    parser.add_argument(
        "--keep-store",
        action="store_true",
        help="Conserva el vector store de File Search al salir.",
    )
    args = parser.parse_args()

    client, deployment = get_client()
    vector_store_id = None
    document_path = os.path.join(
        os.path.dirname(__file__), "demo-data", "politica_viajes_demo.txt"
    )

    try:
        while True:
            print("\n=== AI-3016 · Elegí una herramienta ===")
            for key, label in TOOLS.items():
                print(f"{key}. {label}")
            print("0. Salir")
            choice = input("Opción: ").strip()

            if choice == "0":
                break
            if choice not in TOOLS:
                print("Opción no válida. Elige 1, 2, 3, 4 o 0.")
                continue

            print(f"\nHerramienta elegida: {TOOLS[choice]}")
            if choice == "3":
                print("El modelo responderá usando el documento ficticio de política de viajes.")
            elif choice == "4":
                print(
                    "La función de disponibilidad es simulada. Para verla invocada, "
                    "escribe una fecha, una hora y cuántas personas."
                )

            prompt = input("Escribe tu consulta (o Enter para volver al menú): ").strip()
            if not prompt:
                continue

            try:
                if choice == "1":
                    response = client.responses.create(
                        model=deployment,
                        input=prompt,
                        tools=[
                            {
                                "type": "code_interpreter",
                                "container": {"type": "auto"},
                            }
                        ],
                    )
                    print("\nRespuesta:")
                    print(response.output_text)
                    used = any(x.type == "code_interpreter_call" for x in response.output)
                    print(f"\nCode Interpreter invocado: {'sí' if used else 'no detectado'}")

                elif choice == "2":
                    response = client.responses.create(
                        model=deployment,
                        input=prompt,
                        tools=[{"type": "web_search"}],
                    )
                    print("\nRespuesta:")
                    print(response.output_text)
                    print_sources(response)

                elif choice == "3":
                    if vector_store_id is None:
                        store = client.vector_stores.create(
                            name="AI-3016-Dia-3-Politica-Demo"
                        )
                        vector_store_id = store.id
                        with open(document_path, "rb") as document:
                            client.vector_stores.files.upload_and_poll(
                                vector_store_id=vector_store_id,
                                file=document,
                            )
                        print(f"Documento indexado. Vector store: {vector_store_id}")
                    response = client.responses.create(
                        model=deployment,
                        input=prompt,
                        tools=[
                            {
                                "type": "file_search",
                                "vector_store_ids": [vector_store_id],
                            }
                        ],
                    )
                    print("\nRespuesta:")
                    print(response.output_text)

                elif choice == "4":
                    run_function_calling(client, deployment, prompt)

            except Exception as exc:
                print(f"\nNo se pudo completar esta consulta: {exc}")
                print("Revisa el endpoint, el deployment, los permisos y la herramienta habilitada.")

    finally:
        if vector_store_id:
            if args.keep_store:
                print(f"Vector store conservado: {vector_store_id}")
            else:
                client.vector_stores.delete(vector_store_id)
                print("Vector store temporal eliminado.")


if __name__ == "__main__":
    main()
