import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager

from flask import Flask, jsonify, render_template, request, Response
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
def get_database_path():
    env_path = os.getenv("TRANSCRIPTIONS_DB")
    if env_path:
        return Path(env_path)
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return Path("/tmp/transcriptions.db")
    try:
        local_dir = Path(__file__).parent / "data"
        local_dir.mkdir(parents=True, exist_ok=True)
        return local_dir / "transcriptions.db"
    except OSError:
        return Path("/tmp/transcriptions.db")


DATABASE_PATH = get_database_path()

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
    try:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
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


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#25d366"/>
      <stop offset="100%" stop-color="#128c7e"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="18" fill="url(#g)"/>
  <g transform="translate(12.8, 12.8) scale(1.6)" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="22"/>
  </g>
</svg>"""


@app.get("/favicon.ico")
@app.get("/favicon.svg")
def favicon():
    return Response(FAVICON_SVG, mimetype="image/svg+xml")


@app.get("/")
@app.get("/api/index")
def index():
    return render_template("index.html")


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="O áudio ultrapassa o limite de 100 MB."), 413


@app.get("/api/historico")
def historico():
    # Histórico agora é 100% privado no navegador de cada usuário (localStorage)
    return jsonify([])


@app.delete("/api/historico/<path:_subpath>")
@app.delete("/api/historico")
def limpar_historico(_subpath=None):
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

    mime_type = MIME_TYPES.get(extension, "audio/ogg")
    audio_bytes = audio.read()
    if not audio_bytes:
        return jsonify(error="O arquivo de áudio enviado está vazio."), 400

    try:
        client = genai.Client(api_key=api_key)

        # Otimização 1: Para áudios de até 20 MB, envia bytes direto em memória sem upload intermediário
        if len(audio_bytes) <= 20 * 1024 * 1024:
            audio_content = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        else:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temporary_file:
                temporary_file.write(audio_bytes)
                temporary_path = temporary_file.name
            try:
                audio_content = client.files.upload(
                    file=temporary_path,
                    config=types.UploadFileConfig(mime_type=mime_type),
                )
            finally:
                Path(temporary_path).unlink(missing_ok=True)

        chosen_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        fallback_model = "gemini-3.1-flash-lite"

        # Otimização 2: thinking_budget=0 desativa raciocínio desnecessário, tornando a transcrição ultrarrápida
        gen_config = types.GenerateContentConfig(
            system_instruction="Transcreva estritamente o que for falado no áudio em português com pontuação correta e sem introduções ou explicações. Se não houver fala discernível ou for apenas ruído/silêncio, responda apenas [Áudio inaudível].",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.1,
        )

        def call_model(model_name):
            res = client.models.generate_content(
                model=model_name,
                contents=[audio_content],
                config=gen_config,
            )
            return res.text or ""

        t_start = datetime.now(timezone.utc)
        used_model = chosen_model

        try:
            transcription_text = call_model(chosen_model)
        except Exception as model_err:
            if chosen_model != fallback_model:
                app.logger.warning("Falha ao usar %s (%s). Executando fallback para %s...", chosen_model, model_err, fallback_model)
                used_model = fallback_model
                transcription_text = call_model(fallback_model)
            else:
                raise

        duration_sec = round((datetime.now(timezone.utc) - t_start).total_seconds(), 2)
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        transcription_id = f"tx_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

        return jsonify(
            id=transcription_id,
            filename=Path(audio.filename).name,
            created_at=created_at,
            text=transcription_text,
            duration=duration_sec,
            model=used_model,
        )
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
