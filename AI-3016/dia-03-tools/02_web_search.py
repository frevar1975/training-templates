"""Demo 2: el modelo busca información web y presenta referencias."""
from common import get_client


def main():
    client, deployment = get_client()
    prompt = (
        "Busca tres actividades o lugares para visitar este fin de semana en "
        "Buenos Aires, Argentina. Resume cada opción en una oración, indica "
        "la fecha de consulta y cita las páginas usadas. Si no puedes verificar "
        "la fecha o disponibilidad, dilo claramente."
    )
    response = client.responses.create(
        model=deployment,
        input=prompt,
        tools=[{"type": "web_search"}],
    )

    print("\n=== RESPUESTA ===\n")
    print(response.output_text)

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

    print("\n=== FUENTES DETECTADAS ===")
    if sources:
        for title, url in sources:
            print(f"- {title}: {url}")
    else:
        print("No se encontraron anotaciones de cita en la respuesta.")


if __name__ == "__main__":
    main()
