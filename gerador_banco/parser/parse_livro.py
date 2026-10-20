import json
import yaml

import csv
from pathlib import Path

from gerador_banco.model.edicao_livro import EdicaoLivro


def parse_livro(caminho: Path):
    caminho_indice = caminho / 'indice.csv'
    caminho_informacoes = caminho / 'informacoes.yml'

    with caminho_informacoes.open('r') as arquivo_informacoes:
        informacoes = yaml.safe_load(arquivo_informacoes)

        edicao = EdicaoLivro(
            id_edicao_livro=informacoes['id_edicao_livro'],
            id_livro=informacoes['id_livro'],
            edicao=informacoes['edicao'],
            id_editora=informacoes['id_editora'],
            ano=informacoes['ano'],
            site=informacoes['site'],
            descricao=informacoes['descricao'],
            detalhes=json.dumps(informacoes['detalhes']),
        )
        secoes = informacoes['secoes']

    indices_rows = []
    with caminho_indice.open('r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # consumir header
        try:
            next(reader)
        except StopIteration:
            pass

        for row in reader:
            if not row:
                continue
            
            id_musica = row[0].strip() if len(row) > 0 else ''
            indice = row[1].strip() if len(row) > 1 else ''

            # Converter id para int quando possível
            try:
                id_musica = int(id_musica)
            except Exception:
                id_musica = id_musica

            indices_rows.append([id_musica, str(indice)])

    return edicao, indices_rows, secoes