from dataclasses import dataclass


@dataclass
class Artista:
    id_artista: int
    nome_artistico: str

    def to_tuple(self):
        return self.id_artista, self.nome_artistico
