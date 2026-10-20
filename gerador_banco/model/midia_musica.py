from dataclasses import dataclass

from gerador_banco.model.tipo_midia import TipoMidia


@dataclass
class MidiaMusica:
    id_musica: int
    tipo_midia: TipoMidia
    url: str

    def to_tuple(self):
        return self.id_musica, self.tipo_midia.value, self.url
