import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager

from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
DATABASE_PATH = Path(os.getenv("TRANSCRIPTIONS_DB", Path(__file__).parent / "data" / "transcriptions.db"))

ALLOWED_EXTENSIONS = {".aac", ".flac", ".m4a", ".mp3", ".mp4", ".mpeg", ".mpga", ".oga", ".ogg", ".opus", ".wav", ".webm"}
MIME_TYPES = {
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".mp4": "audio/mp4",
    ".mpeg": "audio/mpeg",
    ".mpga": "audio/mpeg",
    ".oga": "audio/ogg",
    ".ogg": "audio/ogg",
    ".opus": "audio/ogg",
    ".wav": "audio/wav",
    ".webm": "audio/webm",
}


def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    key_file = os.getenv("GEMINI_API_KEY_FILE")
    if key_file:
        try:
            return Path(key_file).read_text(encoding="utf-8").strip()
        except OSError:
            app.logger.exception("Não foi possível ler o arquivo da chave Gemini")
            return None
    return api_key


@contextmanager
def get_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_db():
    with get_db() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )


initialize_db()


@app.get("/")
def index():
    return render_template("index.html")


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="O áudio ultrapassa o limite de 25 MB."), 413


@app.get("/api/historico")
def historico():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT id, filename, text, created_at FROM transcriptions ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.delete("/api/historico/<int:transcription_id>")
def apagar_transcricao(transcription_id):
    with get_db() as connection:
        cursor = connection.execute("DELETE FROM transcriptions WHERE id = ?", (transcription_id,))
    if cursor.rowcount == 0:
        return jsonify(error="Transcrição não encontrada."), 404
    return jsonify(ok=True)


@app.delete("/api/historico")
def limpar_historico():
    with get_db() as connection:
        connection.execute("DELETE FROM transcriptions")
    return jsonify(ok=True)


@app.post("/api/transcrever")
def transcrever():
    api_key = get_api_key()
    if not api_key:
        return jsonify(error="Configure a variável GEMINI_API_KEY antes de iniciar o app."), 503

    audio = request.files.get("audio")
    if not audio or not audio.filename:
        return jsonify(error="Escolha um arquivo de áudio para transcrever."), 400

    extension = Path(audio.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify(error="Formato não aceito. Envie um áudio como OGG, OPUS, MP3, M4A, WAV ou outro formato de áudio comum."), 400

    try:
        client = genai.Client(api_key=api_key)
        suffix = ".ogg" if extension == ".opus" else extension
        temporary_path = None
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
                audio.save(temporary_file)
                temporary_path = temporary_file.name
            uploaded = client.files.upload(
                file=temporary_path,
                config=types.UploadFileConfig(mime_type=MIME_TYPES[extension]),
            )
            
            chosen_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
            fallback_model = "gemini-3.5-transcribe"

            def call_model(model_name):
                if "transcribe" in model_name:
                    res = client.interactions.create(
                        model=model_name,
                        input=[{"type": "audio", "uri": uploaded.uri, "mime_type": uploaded.mime_type}],
                    )
                    return res.output_text or ""
                else:
                    prompt = "Transcreva fielmente todo o áudio a seguir em português com pontuação adequada, sem introduções ou explicações:"
                    res = client.models.generate_content(
                        model=model_name,
                        contents=[uploaded, prompt],
                    )
                    return res.text or ""

            try:
                transcription_text = call_model(chosen_model)
            except Exception as model_err:
                if chosen_model != fallback_model:
                    app.logger.warning("Falha ao usar %s (%s). Executando fallback para %s...", chosen_model, model_err, fallback_model)
                    transcription_text = call_model(fallback_model)
                else:
                    raise

            created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with get_db() as connection:
                cursor = connection.execute(
                    "INSERT INTO transcriptions (filename, text, created_at) VALUES (?, ?, ?)",
                    (Path(audio.filename).name, transcription_text, created_at),
                )
                transcription_id = cursor.lastrowid
            return jsonify(id=transcription_id, filename=Path(audio.filename).name, created_at=created_at, text=transcription_text)
        finally:
            if temporary_path:
                Path(temporary_path).unlink(missing_ok=True)
    except Exception as error:
        app.logger.exception("Falha ao transcrever áudio")
        message = str(error)
        if "401" in message or "API key" in message or "API_KEY" in message:
            message = "A chave do Gemini foi recusada. Confira GEMINI_API_KEY."
        elif "429" in message or "quota" in message.lower():
            message = "O Gemini recusou a solicitação por limite ou cota. Confira sua conta e os limites da API."
        else:
            message = "Não foi possível transcrever este áudio. Confira sua conexão e tente novamente."
        return jsonify(error=message), 502


if __name__ == "__main__":
    app.run(debug=False, port=5000)
