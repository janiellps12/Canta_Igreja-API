from pydantic import BaseModel


class ContaCriadaResponse(BaseModel):
    slug: str
    email: str
    nome: str
    subject: str
    provider: str
