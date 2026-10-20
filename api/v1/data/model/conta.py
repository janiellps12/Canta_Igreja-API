import dataclasses

from api.v1.data.rest.conta_criada_response import ContaCriadaResponse


@dataclasses.dataclass
class Conta:
    id: int

    slug: str
    email: str

    nome: str

    subject: str
    provider: str

    def json(self):
        return ContaCriadaResponse(
            slug=self.slug,
            email=self.email,
            nome=self.nome,
            subject=self.subject,
            provider=self.provider
        ).model_dump()
