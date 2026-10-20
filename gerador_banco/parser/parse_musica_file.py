from pathlib import Path
from typing import List, Dict, Optional

from gerador_banco.model.artista import Artista
from gerador_banco.model.composicao_musica import ComposicaoMusica
from gerador_banco.model.midia_musica import MidiaMusica
from gerador_banco.model.musica import Musica
from gerador_banco.model.tipo_composicao import TipoComposicao
from gerador_banco.model.tipo_midia import TipoMidia


def parse_musica_file(file_path: Path, artistas: Dict[str, Artista]):
    texto = file_path.read_text()
    cabecalho, letra = texto.split('\n\n', maxsplit=1)

    dados = dict()
    for linha in cabecalho.split('\n'):
        chave, conteudo = linha.split(': ', maxsplit=1)
        dados[chave] = conteudo.split('; ')

    musica = Musica(
        id_musica=int(dados['Índice'][0]),
        titulo=dados['Título'][0],
        letra=letra.strip(),
        tonalidade_sugerida=dados['Tonalidade'][0] if 'Tonalidade' in dados else None,
        colaboradores=gerar_contribuidores_json(dados),
        midias=gerar_midias_json(dados),
        rotulos=gerar_rotulos_json(dados['Rótulos']),
        arquivo_origem=file_path,
    )

    musica.validate()

    midias: List[MidiaMusica] = []
    midias += gerar_midias(dados, musica, TipoMidia.YouTube)
    midias += gerar_midias(dados, musica, TipoMidia.CifraClub)
    midias += gerar_midias(dados, musica, TipoMidia.Partitura)

    composicoes: List[ComposicaoMusica] = []
    composicoes += gerar_composicoes_musica(dados, musica, artistas, TipoComposicao.Composicao, 'Compositores')
    composicoes += gerar_composicoes_musica(dados, musica, artistas, TipoComposicao.Letra, 'Letristas')
    composicoes += gerar_composicoes_musica(dados, musica, artistas, TipoComposicao.Melodia, 'Musicistas')

    return musica, midias, composicoes


def gerar_midias(dados: dict, musica: Musica, tipo_midia: TipoMidia) -> List[MidiaMusica]:
    chave = tipo_midia.name
    if chave in dados and dados[chave]:
        return [MidiaMusica(musica.id_musica, tipo_midia, url) for url in dados[chave] if url != '']

    return []

def gerar_midias_json(dados: dict) -> Dict:
    midias = {}

    for tipo_midia in TipoMidia:
        chave = tipo_midia.name

        if chave in dados and dados[chave]:
            raw_items = [c.strip() for c in dados[chave] if c.strip() != '']

            # Normaliza e expande itens que podem conter múltiplos valores separados por ';'
            conteudos: List[str] = []
            for item in raw_items:
                if tipo_midia == TipoMidia.YouTube:
                    item = item.replace('https://www.youtube.com/watch?v=', '') \
                               .replace('https://youtu.be/', '')

                parts = [p.strip() for p in item.split(';') if p.strip() != '']
                conteudos.extend(parts)

            if conteudos:
                midias[chave] = conteudos[0]
                if tipo_midia == TipoMidia.YouTube:
                    midias[f'{chave}s'] = conteudos


    return midias


def gerar_composicoes_musica(dados: dict, musica: Musica, artistas: Dict[str, Artista], tipo_composicao: TipoComposicao, chave: str) -> List[ComposicaoMusica]:
    if chave not in dados and dados[chave]:
        return []

    composicoes: List[ComposicaoMusica] = []
    for nome_artista in dados[chave]:
        if nome_artista.strip() == '':
            continue

        if nome_artista in artistas:
            artista = artistas[nome_artista]
            composicao = ComposicaoMusica(musica.id_musica, artista.id_artista, tipo_composicao, None)
        else:
            composicao = ComposicaoMusica(musica.id_musica, None, tipo_composicao, nome_artista)

        composicoes.append(composicao)

    return composicoes

def gerar_contribuidores_json(dados: dict) -> List[ComposicaoMusica]:
    compositores = {}

    for tipo_composicao in TipoComposicao:
        chave = tipo_composicao.value

        if chave in dados and dados[chave]:
            pessoas = [pessoa.strip() for pessoa in dados[chave] if pessoa.strip() != '']

            if pessoas:
                compositores[chave.lower()] = pessoas

    return compositores

def gerar_rotulos_json(rotulos: Optional[List[str]]) -> List[str]:
    rotulos = rotulos if rotulos else []
    rotulos = rotulos if rotulos != [""] else []

    return rotulos
