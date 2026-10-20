import json

import sentry_sdk
from flask import Flask, jsonify
from flask_cors import CORS
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
