from dataclasses import dataclass
from typing import Optional


@dataclass
class EdicaoLivro:
    id_edicao_livro: int
    id_livro: int
    edicao: str
    id_editora: int
    ano: int
    site: Optional[str]
    descricao: str
    detalhes: str

    def to_tuple(self):
        return self.id_edicao_livro, self.id_livro, self.edicao, self.id_editora, self.ano, self.site, self.descricao, self.detalhes
