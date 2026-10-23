import os
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, render_template, request, send_file
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-demo-change-me")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "mp4", "ogg", "webm", "flac"}
LANGUAGES = {
    "es-BO": "Español (Bolivia)",
    "es-ES": "Español (España)",
    "es-MX": "Español (México)",
    "en-US": "English (United States)",
}


def check_config():
    missing = [name for name in ("SPEECH_KEY", "SPEECH_REGION") if not os.getenv(name)]
    if missing:
        raise RuntimeError("Faltan variables de entorno: " + ", ".join(missing))


def transcribe_audio(audio_path: str, language: str) -> str:
    """Transcribe one uploaded audio file using Azure Speech SDK."""
    import azure.cognitiveservices.speech as speechsdk

    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["SPEECH_KEY"],
        region=os.environ["SPEECH_REGION"],
    )
    speech_config.speech_recognition_language = language
    audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speechsdk.ResultReason.NoMatch:
        return ""
    if result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.CancellationDetails(result)
        message = details.error_details or str(details.reason)
        raise RuntimeError(f"Azure Speech no pudo completar la transcripción: {message}")
    raise RuntimeError(f"La transcripción terminó con un estado inesperado: {result.reason}")


def to_pcm_wav(source_path: str, destination_path: str) -> None:
    """Normalize audio to the PCM WAV format expected by the Speech SDK."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", source_path,
             "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", destination_path],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("No encuentro ffmpeg. Instálalo y vuelve a abrir la terminal.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("La conversión del audio tardó demasiado. Prueba con un archivo más corto.") from exc
    if result.returncode != 0:
        detail = result.stderr.strip()[-500:]
        raise RuntimeError("No pude convertir el audio. Verifica que el archivo se pueda reproducir. " + detail)


@app.errorhandler(413)
def file_too_large(_error):
    return render_template("index.html", languages=LANGUAGES, error="El archivo supera el límite de 25 MB."), 413


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", languages=LANGUAGES)

    audio = request.files.get("audio")
    language = request.form.get("language", "es-BO")
    if language not in LANGUAGES:
        language = "es-BO"
    if not audio or not audio.filename:
        return render_template("index.html", languages=LANGUAGES, error="Selecciona un archivo de audio.")

    filename = secure_filename(audio.filename)
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix not in ALLOWED_EXTENSIONS:
        return render_template("index.html", languages=LANGUAGES, error="Formato no admitido. Usa WAV, MP3, M4A, MP4, OGG, WEBM o FLAC.")

    try:
        check_config()
        with tempfile.TemporaryDirectory(prefix="speech-demo-") as workdir:
            original_path = os.path.join(workdir, filename or "audio." + suffix)
            wav_path = os.path.join(workdir, "audio-normalizado.wav")
            audio.save(original_path)
            if os.path.getsize(original_path) == 0:
                raise RuntimeError("El archivo está vacío.")
            to_pcm_wav(original_path, wav_path)
            transcript = transcribe_audio(wav_path, language)
        if not transcript:
            return render_template("index.html", languages=LANGUAGES, error="No se detectó voz. Prueba con un audio más claro.")
        return render_template(
            "index.html", languages=LANGUAGES, transcript=transcript,
            filename=filename, language=language,
        )
    except Exception as exc:
        app.logger.exception("Speech demo failed")
        return render_template("index.html", languages=LANGUAGES, error=str(exc)), 400


@app.route("/download", methods=["POST"])
def download():
    transcript = request.form.get("transcript", "")
    if not transcript.strip():
        flash("No hay una transcripción para descargar.", "error")
        return render_template("index.html", languages=LANGUAGES), 400
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt", delete=False) as f:
        f.write(transcript)
        path = f.name
    response = send_file(path, as_attachment=True, download_name="transcripcion.txt", mimetype="text/plain; charset=utf-8")
    response.call_on_close(lambda: os.unlink(path) if os.path.exists(path) else None)
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
