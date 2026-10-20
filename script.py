import argparse
import csv
from pathlib import Path
from typing import Dict

from gerador_banco.model.artista import Artista

parser = argparse.ArgumentParser(description='Gerador documento')

parser.add_argument('caminho_banco', type=str, help='Caminho e nome do arquivo do banco')

args = parser.parse_args()

# ---------------
origem = Path('api/public/biblioteca/obras/1.sqlite')
destino = Path(args.caminho_banco)
# ---------------

def carregar_artistas(caminho: Path) -> Dict[str, Artista]:
    artistas: Dict[str, Artista] = dict()

    with open(caminho, 'r') as arquivo:
        reader = csv.DictReader(arquivo)

        for row in reader:
            artista = Artista(id_artista=row['id'], nome_artistico=row['nome'])
            artistas[artista.nome_artistico] = artista

    return artistas


# caminho_artistas = Path(args.caminho_dados) / 'artistas.csv'

# artistas = carregar_artistas(caminho_artistas)
# midias: List[MidiaMusica] = []
# composicoes: List[ComposicaoMusica] = []

import subprocess
subprocess.call("python build_api.py --estrategia=completa --obra=1", shell=True)

# banco = Banco(caminho_banco)
# banco.conectar()
# [...]
# banco.cadastrar_artistas(artistas.values())
# banco.cadastrar_midias_musicas(midias)
# banco.cadastrar_composicoes_musicas(composicoes)
# [...]
# banco.desconectar()

import shutil

shutil.copyfile(origem, destino)