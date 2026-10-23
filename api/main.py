import json
import re
from functools import lru_cache
from pathlib import Path

import sentry_sdk
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException

from api.configuration import Configuration
from api.v1.index import init

app = Flask(__name__)
CORS(app, origins=Configuration.cors)

app.config["SQLALCHEMY_DATABASE_URI"] = Configuration.posgres_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

sentry_sdk.init(
    dsn=Configuration.sentry_dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=0.01,
    integrations=[FlaskIntegration()]
)

db = SQLAlchemy(app)

init(app, db)


@lru_cache(maxsize=1)
def carregar_catalogo():
    pasta = Path(__file__).resolve().parent.parent / "dados" / "musicas"
    arquivos = sorted(pasta.glob("*.txt"), key=lambda p: p.stem)
    if not arquivos:
        raise FileNotFoundError("A pasta dados/musicas não foi incluída na publicação")
    musicas = []
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        cabecalho, separador, letra = texto.partition("\n\n")
        campos = dict(linha.split(":", 1) for linha in cabecalho.splitlines() if ":" in linha)
        campos = {k.strip(): v.strip() for k, v in campos.items()}
        titulo = campos.get("Título", "").strip()
        if not separador or not titulo or not letra.strip():
            raise ValueError(f"Formato inválido em {arquivo.name}; publicação não foi importada parcialmente")
        # Preservar o original e converter apenas o negrito de refrão para o leitor.
        letra_leitura = re.sub(r"\*\*(.*?)\*\*", lambda m: "\n\n[Refrão]\n" + m.group(1) + "\n\n", letra.strip(), flags=re.S)
        musicas.append({
            "id": arquivo.stem,
            "title": titulo,
            "lyrics": letra_leitura,
            "lyrics_original": letra.strip(),
            "number": "",
            "source_index": campos.get("Índice", arquivo.stem),
            "composer": campos.get("Compositores", ""),
            "video": campos.get("YouTube", ""),
            "tone": campos.get("Tonalidade", ""),
            "tags": [r.strip() for r in campos.get("Rótulos", "").split(";") if r.strip()],
        })
    return musicas


@app.route("/v1/catalogo", methods=["GET"])
@cross_origin(origins="*")
def obter_catalogo():
    try:
        pagina = int(request.args.get("page", "1"))
        tamanho = int(request.args.get("per_page", "100"))
    except ValueError:
        return jsonify({"error": "page e per_page devem ser números inteiros"}), 400
    if pagina < 1 or tamanho < 1 or tamanho > 200:
        return jsonify({"error": "page deve ser positivo; per_page deve ficar entre 1 e 200"}), 400
    try:
        musicas = carregar_catalogo()
    except (OSError, ValueError):
        app.logger.exception("Não foi possível carregar o catálogo")
        return jsonify({"error": "Catálogo indisponível. Consulte os logs da função."}), 503
    inicio = (pagina - 1) * tamanho
    return jsonify({
        "songs": musicas[inicio:inicio + tamanho],
        "total": len(musicas),
        "page": pagina,
        "per_page": tamanho,
        "next_page": pagina + 1 if inicio + tamanho < len(musicas) else None,
    })


@app.errorhandler(404)
def error404(e):
    return jsonify({"status": 404}), 404


@app.errorhandler(ValidationError)
def handle_exception(e):
    return jsonify({
        "code": 400,
        "debug": json.loads(e.json())
    }), 400


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    app.run(debug=True)
