import html
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, model_validator, field_validator
from typing_extensions import Self


class ItemRepertorio(BaseModel):
    id_musica: Optional[int] = None
    termo: Optional[str] = None
    momento: Optional[str] = None
    tonalidade: Optional[str] = None

    @field_validator("termo", "momento", "tonalidade", mode="before")
    @classmethod
    def transform(cls, raw: Optional[str]) -> Optional[str]:
        return html.escape(raw, quote=False) if raw else None

    @model_validator(mode='after')
    def check_item_repertorio_tipo(self) -> Self:
        if self.id_musica is None and self.termo is None:
            raise ValueError(f"missing id_musica and termo: it is necessary to define at least one or them")
        return self


class ContaReference(BaseModel):
    nome: str
    slug: str


class RepertorioMetadataDiaLiturgico(BaseModel):
    id_romcal: str
    ano: str


class RepertorioMetadata(BaseModel):
    data: Optional[date] = None
    dia_liturgico: Optional[RepertorioMetadataDiaLiturgico] = None


class RepertorioBaseModel(BaseModel):
    titulo: str

    @field_validator("titulo", mode="before")
    @classmethod
    def transform(cls, raw: str) -> str:
        return html.escape(raw, quote=False)

    itens: List[ItemRepertorio]

    metadata: Optional[RepertorioMetadata] = None

class RepertorioRequest(RepertorioBaseModel):
    pass


class RepertorioResponse(RepertorioBaseModel):
    slug: str
    conta: ContaReference

    criado_em: str
    atualizado_em: Optional[str] = None
