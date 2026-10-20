import json

from dataclasses import dataclass


@dataclass
class Obra:
    id_obra: int
    titulo: str
    descricao: str

    crc32: int
    disponivel: bool

    def to_json(self):
        return {
            "id_obra": self.id_obra,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "crc32": self.crc32,
            "disponivel": self.disponivel
        }
    
    def to_tuple(self):
        return (self.id_obra, self.titulo, self.descricao, self.crc32)
