from api.v1.data.model.conta import Conta
from api.v1.data.rest.repertorio_rest import RepertorioRequest
from api.v1.repository.repertorio_repository import RepertorioRepository


class RepertorioService:

    def __init__(self, db):
        self.repository = RepertorioRepository(db)

    def find_by(self, conta: str, repertorio: str):
        return self.repository.select_repertorio_publico(conta, repertorio)

    def criar(self, conta: Conta, repertorio: RepertorioRequest):
        return self.repository.create(conta, repertorio)

    def atualizar(self, conta: Conta, repertorio_slug: str, repertorio: RepertorioRequest):
        return self.repository.update(conta, repertorio_slug, repertorio)
