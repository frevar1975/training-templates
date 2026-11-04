"""Demo 4: la app atiende una llamada de función con datos ficticios."""
import json

from common import get_client


def consultar_disponibilidad(fecha, hora, personas):
    """Función local simulada; no consulta un servicio ni confirma reservas."""
    return {
        "fecha_solicitada": fecha,
        "hora_solicitada": hora,
        "personas_solicitadas": personas,
        "hay_disponibilidad": True,
        "lugares_disponibles_demo": 6,
        "nota": "Resultado ficticio para la demostración; no es una reserva real.",
    }


TOOL = {
    "type": "function",
    "name": "consultar_disponibilidad",
    "description": (
        "Consulta la disponibilidad ficticia de una visita guiada. "
        "No realiza ni confirma una reserva."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "fecha": {
                "type": "string",
                "description": "Fecha solicitada en formato AAAA-MM-DD.",
            },
            "hora": {
                "type": "string",
                "description": "Hora solicitada en formato HH:MM.",
            },
            "personas": {
                "type": "integer",
                "description": "Cantidad de personas.",
            },
        },
        "required": ["fecha", "hora", "personas"],
        "additionalProperties": False,
    },
}


def main():
    client, deployment = get_client()
    prompt = (
        "Consulta si hay lugar para una visita guiada en Buenos Aires "
        "el sábado 7 de noviembre de 2026 a las 10:00 para 2 personas. "
        "No reserves: solo consulta la disponibilidad."
    )
    instructions = (
        "Responde en español. Si necesitas disponibilidad, usa la función. "
        "Aclara que la información recibida es ficticia y que no se hizo una reserva."
    )
    response = client.responses.create(
        model=deployment,
        instructions=instructions,
        input=prompt,
        tools=[TOOL],
    )

    tool_outputs = []
    for item in response.output:
        if item.type == "function_call" and item.name == "consultar_disponibilidad":
            arguments = json.loads(item.arguments)
            print("=== EL MODELO SOLICITÓ ESTA FUNCIÓN ===")
            print(json.dumps(arguments, ensure_ascii=False, indent=2))
            result = consultar_disponibilidad(**arguments)
            print("\n=== LA APLICACIÓN EJECUTÓ LA FUNCIÓN LOCAL ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

    if not tool_outputs:
        print("El modelo no solicitó la función en esta ejecución.")
        print(response.output_text)
        return

    final_response = client.responses.create(
        model=deployment,
        previous_response_id=response.id,
        input=tool_outputs,
        tools=[TOOL],
        instructions=instructions,
    )
    print("\n=== RESPUESTA FINAL DEL MODELO ===\n")
    print(final_response.output_text)


if __name__ == "__main__":
    main()
