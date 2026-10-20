import json
from pathlib import Path
from typing import List
import zlib

from dataclasses import dataclass
from gerador_banco.util.rotulos import Rotulos


@dataclass
class Musica:
    id_musica: int
    titulo: str
    letra: str
    tonalidade_sugerida: str

    colaboradores: list
    midias: list
    rotulos: List[str]

    arquivo_origem: Path

    def validate(self):
        if str(self.arquivo_origem.stem) != str(self.id_musica):
            raise ValueError(f"Música {self.id_musica}: O id da música não corresponde a nome do arquivo '{self.arquivo_origem}'")
        
        try:
            Rotulos.validar_rotulos(self.rotulos)
        except ValueError as e:
            raise ValueError(f"Música {self.id_musica}: {e}")

    def to_tuple(self):
        return self.id_musica, self.titulo, self.letra, json.dumps(self.colaboradores), json.dumps(self.midias), self.crc32(), json.dumps(self.rotulos)

    def to_json(self):
        return {
            "id_musica": self.id_musica,
            "titulo": self.titulo,
            "letra": self.letra,
            "tonalidade_sugerida": self.tonalidade_sugerida,
            "colaboradores": self.colaboradores,
            "rotulos": self.rotulos,
            "midias": self.midias,
            "crc32": self.crc32()
        }

    def crc32(self):
        return zlib.crc32(f'{self.titulo}-{self.letra}-{self.tonalidade_sugerida}-{self.colaboradores}-{self.midias}-{self.rotulos}'.encode())

    def __hash__(self):
        return hash(self.crc32())
    
    def is_vazia(self):
        return self.letra is None or self.letra.strip() == ""
