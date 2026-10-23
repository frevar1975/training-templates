"""Genera dos WAV de prueba en español boliviano con el recurso Azure Speech del .env."""
import os
from pathlib import Path

from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()
key = os.getenv("SPEECH_KEY")
region = os.getenv("SPEECH_REGION")
if not key or not region:
    raise SystemExit("Configura SPEECH_KEY y SPEECH_REGION en el archivo .env antes de ejecutar.")

samples = [
    {
        "filename": "01-confirmacion-cita-es-BO.wav",
        "textfile": "01-confirmacion-cita-es-BO.txt",
        "voice": "es-BO-SofiaNeural",
        "text": (
            "Hola, señora Camila. Le llamo de la Clínica San Gabriel para confirmar "
            "su cita de mañana a las diez y media de la mañana. Por favor, llegue "
            "quince minutos antes y traiga su carnet de identidad. Si necesita "
            "cambiar el horario, puede llamarnos al siete cero ocho, cuatro cinco "
            "seis, siete ocho nueve. Muchas gracias."
        ),
    },
    {
        "filename": "02-consulta-pedido-es-BO.wav",
        "textfile": "02-consulta-pedido-es-BO.txt",
        "voice": "es-BO-MarceloNeural",
        "text": (
            "Buenas tardes. Mi nombre es Diego Rojas y llamo para consultar por "
            "el pedido número B, cuatro, ocho, dos, nueve. La entrega estaba "
            "programada para el martes, pero todavía no recibí el paquete. "
            "¿Podrían verificar el estado y enviarme una actualización por correo? "
            "Mi dirección es diego punto rojas arroba ejemplo punto com. Gracias."
        ),
    },
]

for sample in samples:
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = sample["voice"]
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )
    output_path = Path(sample["filename"])
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )
    result = synthesizer.speak_text_async(sample["text"]).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = speechsdk.SpeechSynthesisCancellationDetails.from_result(result)
        error = details.error_details or str(details.reason)
        if output_path.exists():
            output_path.unlink()
        raise SystemExit(f"No se pudo generar {output_path.name}: {error}")
    Path(sample["textfile"]).write_text(sample["text"] + "\n", encoding="utf-8")
    print(f"Listo: {output_path.name} ({sample['voice']})")

print("Carga los WAV en el demo y selecciona Español (Bolivia).")
