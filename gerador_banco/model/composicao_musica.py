from dataclasses import dataclass
from typing import Optional

from gerador_banco.model.tipo_composicao import TipoComposicao


@dataclass
class ComposicaoMusica:
    id_musica: int
    id_artista: Optional[int]
    id_tipo_composicao: Optional[TipoComposicao]
    adaptacao: Optional[str]

    def to_tuple(self):
        return self.id_musica, self.id_artista, self.id_tipo_composicao.value, self.adaptacao
