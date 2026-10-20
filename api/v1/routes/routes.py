from flask import jsonify, request
from werkzeug.exceptions import Unauthorized, NotFound

from api.v1.data.rest.repertorio_rest import RepertorioRequest
from api.v1.service.auth_service import AuthService
from api.v1.service.repertorio_service import RepertorioService


def routes(app, db):

    @app.route("/v1/auth", methods=["POST"])
    def auth():
        """
        Criar usuário caso não exista
        """
        conta = AuthService(db).auth(request.headers.get('Authorization'), request.headers.get('X-app-origin'))
        return jsonify(conta.json()), 200

    @app.route("/v1/repertorios/<conta_slug>", methods=["POST"])
    def post_repertorio(conta_slug):
        """
        Criar um repertório novo
        """
        conta = AuthService(db).auth(request.headers.get('Authorization'), request.headers.get('X-app-origin'))

        repertorio = RepertorioRequest(**request.json)

        if conta.slug != conta_slug:
            raise Unauthorized()

        repertorio_criado = RepertorioService(db).criar(conta, repertorio)

        return jsonify(repertorio_criado.model_dump()), 200

    @app.route("/v1/repertorios/<conta_slug>/<repertorio_slug>", methods=["PUT"])
    def patch_repertorio(conta_slug, repertorio_slug):
        """
        Atualizar um repertório existente
        """
        conta = AuthService(db).auth(request.headers.get('Authorization'), request.headers.get('X-app-origin'))

        repertorio = RepertorioRequest(**request.json)

        if conta.slug != conta_slug:
            raise Unauthorized()

        repertorio_atualizado = RepertorioService(db).atualizar(conta, repertorio_slug, repertorio)

        if repertorio_atualizado is None:
            raise NotFound()

        return jsonify(repertorio_atualizado.model_dump()), 200

    @app.route("/v1/repertorios/<conta>/<repertorio>", methods=["GET"])
    def get_repertorio(conta, repertorio):
        """
        Obter um repertório
        """
        repertorio = RepertorioService(db).find_by(conta, repertorio)

        if repertorio is None:
            raise NotFound()

        return jsonify(repertorio.model_dump()), 200
