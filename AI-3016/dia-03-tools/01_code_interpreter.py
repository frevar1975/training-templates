"""Demo 1: el modelo usa un entorno de código para resolver un cálculo."""
from common import get_client


def main():
    client, deployment = get_client()
    prompt = (
        "Analiza estas ventas ficticias en pesos argentinos: enero 120000, "
        "febrero 155000, marzo 141000, abril 190000. Calcula el total, "
        "el promedio y el porcentaje de crecimiento entre enero y abril. "
        "Explica brevemente los pasos y aclara que son datos inventados."
    )
    response = client.responses.create(
        model=deployment,
        input=prompt,
        tools=[{"type": "code_interpreter", "container": {"type": "auto"}}],
    )

    print("\n=== RESPUESTA ===\n")
    print(response.output_text)
    print("\n=== HERRAMIENTAS INVOCADAS ===")
    calls = [item for item in response.output if item.type == "code_interpreter_call"]
    print(f"Code Interpreter: {'sí' if calls else 'no detectado'}")


if __name__ == "__main__":
    main()
