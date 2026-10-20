from collections import defaultdict
import os
import sqlite3
from pathlib import Path
from typing import List, Iterable, Dict, Any

from gerador_banco.model.artista import Artista
from gerador_banco.model.composicao_musica import ComposicaoMusica
from gerador_banco.model.edicao_livro import EdicaoLivro
from gerador_banco.model.midia_musica import MidiaMusica
from gerador_banco.model.musica import Musica
from gerador_banco.model.obra import Obra


class Banco:

    def __init__(self, nome='cantaIgreja.db'):
        self.nome = nome
        self.conexao: sqlite3.Connection = None

    def conectar(self):
        self.conexao = sqlite3.connect(self.nome)

    def desconectar(self):
        self.conexao.close()

    def popular_banco(self, migration_path: Path):
        migrations = [
            migration_path / nome_arquivo
            for nome_arquivo in sorted(os.listdir(migration_path))
            if nome_arquivo.startswith('v')
        ]
        
        self.aplicar_migrations(migrations)

    def aplicar_migrations(self, migrations: List[Path]):
        cursor = self.conexao.cursor()

        for migration in migrations:
            if migration is None:
                continue

            print('Migrate:', migration)

            sql = migration.read_text()
            cursor.executescript(sql)
        
        cursor.close()

    def popular_musicas(self, migration_path: Path):
        cursor = self.conexao.cursor()

        for nome_arquivo in os.listdir(migration_path):
            arquivo = migration_path / nome_arquivo
            sql = arquivo.read_text()
            cursor.execute(sql)

        cursor.close()

    def cadastrar_artistas(self, artistas: Iterable[Artista]):
        # return self._cadastrar(
        #     'INSERT INTO artista VALUES (?, ?)',
        #     artistas
        # )
        pass

    def cadastrar_musicas(self, musicas: Iterable[Musica]):
        return self._cadastrar(
            'INSERT INTO musica VALUES (?, ?, ?, ?, ?, ?, ?)',
            musicas
        )

    def cadastrar_midias_musicas(self, midias_musicas: Iterable[MidiaMusica]):
        # return self._cadastrar(
        #     'INSERT INTO midia_musica (id_musica, id_tipo_midia, url) VALUES (?, ?, ?)',
        #     midias_musicas
        # )
        pass

    def cadastrar_composicoes_musicas(self, composicoes_musicas: Iterable[ComposicaoMusica]):
        # return self._cadastrar(
        #     'INSERT INTO composicao_musica (id_musica, id_artista, id_tipo_composicao, adaptacao) VALUES (?, ?, ?, ?)',
        #     composicoes_musicas
        # )
        pass

    def cadastrar_indices(self, indices: Dict[int, list]):
        for id, indice in indices.items():
            tuplas = [(id, *tupla, ordem+1) for ordem, tupla in enumerate(indice)]

            contagem_musicas = defaultdict(lambda: 0)
            for tupla in tuplas:
                contagem_musicas[tupla[1]] += 1
            musicas_referenciadas_mais_de_uma_vez = list(filter(lambda it: contagem_musicas[it] > 1, contagem_musicas.keys()))
            if musicas_referenciadas_mais_de_uma_vez:
                print(f'Livro de id {tuplas[0][0]} - músicas referenciadas mais de uma vez: {musicas_referenciadas_mais_de_uma_vez}')

            self._cadastrar_tuplas(
                'INSERT INTO cantico_livro (id_edicao_livro, id_musica, indice, ordem) VALUES (?, ?, ?, ?)',
                tuplas
            )

    def registrar_obra(self, obra: Obra):
        return self._cadastrar(
            '''
            INSERT INTO exemplar_biblioteca(id_obra, titulo, descricao, crc32)
                 VALUES (?, ?, ?, ?)
            ''',
            [obra]
        )

    def testar_scripts(self):
        cursor = self.conexao.cursor()

        values = cursor.execute("""
        SELECT rowid,
               snippet(musica_busca, 0, '||', '||', '', 12) as titulo,
               snippet(musica_busca, 1, '||', '||', '', 12) as inicio_letra
       FROM musica_busca
      WHERE musica_busca MATCH ?
       ORDER BY rank""", ['contrição']).fetchall()

        for value in values:
            print(value)

        # values = cursor.execute("""
        # SELECT id_edicao_livro, count(*)
        #  FROM cantico_livro
        # GROUP BY id_edicao_livro
        # """).fetchall()

        # for value in values:
        #     print(value)
        cursor.close()

    def cadastrar_edicoes_livros(self, edicoes_livros: Dict[int, EdicaoLivro]):
        self._cadastrar_tuplas(
            'INSERT INTO edicao_livro (id_edicao_livro, id_livro, edicao, id_editora, ano, site, descricao, detalhes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            [edicao.to_tuple() for edicao in edicoes_livros.values()]
        )

    def cadastrar_secoes_livros(self, secoes_livros: Dict[int, Dict[str, List[Any]]]):
        tuplas_secoes = []
        tuplas_secoes_musicas = []

        id_secao = 0
        for id_edicao_livro, secoes_livro in secoes_livros.items():
            ordem = 0
            for titulo in secoes_livro.keys():
                id_secao += 1
                ordem += 1
                tuplas_secoes.append((id_secao, id_edicao_livro, titulo, ordem))
                indices = tuple(str(indice) for indice in secoes_livro[titulo])

                if len(indices) == 1:
                    ids_musicas = self._buscar(f'''
                        SELECT id_musica FROM cantico_livro
                        WHERE id_edicao_livro = ?
                        AND indice = {indices[0]}
                        ORDER BY ordem
                        ''',
                        id_edicao_livro
                    )
                else:
                    ids_musicas = self._buscar(f'''
                        SELECT id_musica FROM cantico_livro
                        WHERE id_edicao_livro = ?
                        AND indice in {indices}
                        ORDER BY ordem
                        ''',
                        id_edicao_livro
                    )
                tuplas_secoes_musicas += [(id_secao, id_musica[0], id_edicao_livro) for id_musica in ids_musicas]

        self._cadastrar_tuplas(
            'INSERT INTO secao_edicao_livro (id_secao_edicao_livro, id_edicao_livro, titulo, ordem) VALUES (?, ?, ?, ?)',
            tuplas_secoes
        )

        self._cadastrar_tuplas(
            'INSERT INTO cantico_secao (id_secao_edicao_livro, id_musica, id_edicao_livro) VALUES (?, ?, ?)',
            tuplas_secoes_musicas
        )

    def crc32_sum_musicas(self):
        cursor = self.conexao.cursor()

        values = cursor.execute("SELECT sum(crc32) FROM musica").fetchall()

        return values[0][0]

    def _cadastrar(self, sql: str, entidades: Iterable):
        tuplas = map(lambda it: it.to_tuple(), entidades)
        return self._cadastrar_tuplas(sql, tuplas)

    def _cadastrar_tuplas(self, query: str, tuplas: Iterable):
        cursor = self.conexao.cursor()

        cursor.executemany(query, tuplas)
        self.conexao.commit()

        cursor.close()

    def _buscar(self, query, *args):
        cursor = self.conexao.cursor()
        response = cursor.execute(query, args).fetchall()
        cursor.close()

        return response