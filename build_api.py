import argparse
import glob
import json
import os
import yaml
import zlib

from gerador_banco.model.edicao_livro import EdicaoLivro
from tqdm import tqdm

from pathlib import Path
from typing import List, Dict

from gerador_banco.parser.parse_musica_file import parse_musica_file
from gerador_banco.parser.parse_livro import parse_livro

from gerador_banco.bd.banco import Banco
from gerador_banco.model.musica import Musica
from gerador_banco.model.obra import Obra
from gerador_banco.repertorios import FESTAS_FIXAS, gerar_previa, crc32_arquivo, gerar_indices
from gerador_banco.util.rotulos import Rotulos

parser = argparse.ArgumentParser(description='Gerador documento')
parser.add_argument('--estrategia', dest="estrategia", type=str, default='simplificada', help='simplificada | completa')
parser.add_argument('--obra', dest="obra", type=str, default=None, help='todas | id')

args = parser.parse_args()


caminho_musicas = Path('dados/musicas/')
destino_musicas = Path('api/public/musicas/')


def get_titulo_musica(id_musica: int) -> str:
    """Lê o título da música a partir do arquivo .txt correspondente."""
    path = caminho_musicas / f"{id_musica}.txt"
    if not path.exists():
        raise Exception(f"Música {id_musica} presente em obra, mas não encontra-se no catálogo de músicas revisadas (./{caminho_musicas}/)")

    for linha in path.read_text(encoding="utf-8").splitlines():
        if linha.startswith("Título: "):
            return linha[len("Título: "):].strip()
    
    raise Exception(f"Título não encontrado para música {id_musica} no arquivo {path}")


def gerar_resumo(itens: list) -> str:
    """Gera resumo com os títulos das 3 primeiras músicas não ignoradas."""
    nao_ignorados = [it for it in itens if not it.get('metadata', {}).get('ignorar', False)]
    total = len(nao_ignorados)

    if total == 0:
        raise Exception(f"Repertório sem músicas (itens ignorados: {len(itens)})")

    titulos = []
    for item in nao_ignorados:
        titulos.append(get_titulo_musica(item['id_musica']))
        if len(titulos) == 3:
            break

    if total == 1:
        return titulos[0]
    elif total == 2:
        return f"{titulos[0]} e {titulos[1]}"
    elif total == 3:
        return f"{titulos[0]}, {titulos[1]} e {titulos[2]}"
    else:
        restantes = total - 3
        return ", ".join(titulos) + f" e mais {restantes} sugest{'ão' if restantes == 1 else 'ões'}"


caminho_obras = Path('dados/obras/')
destino_obras = Path('api/public/biblioteca/obras/')

arquivos_obra = os.listdir(caminho_obras)


# =========================
# Músicas .json
# =========================

verificacao_musicas_txt = set()
verificacao_musicas_persistidas = set()

# i = 0
arquivos_musica = os.listdir(caminho_musicas)
for nome_arquivo in arquivos_musica:
    path = caminho_musicas / nome_arquivo
    verificacao_musicas_txt.add(int(path.stem))
    # i+=1
    # if i > 5:
    #     break
    try:
        [musica, _, _] = parse_musica_file(path, {})
    except Exception as e:
        print(f'Error with file: {path}\n')
        raise e


    if musica.letra == "":
        continue
    
    if musica.is_vazia():
        continue

    destino = destino_musicas / f"{musica.id_musica}.json"
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(musica.to_json(), f, ensure_ascii=False, indent=4)

# =========================
# Dump das obras
# =========================
obras = []
todas_musicas_elegiveis = set()
indices_todas_obras: Dict[int, list] = {}
edicoes_todas_obras: Dict[int, EdicaoLivro] = {}
secoes_todas_obras: Dict[int, Dict[str, List[int]]] = {}

caminho_migrations = Path('gerador_banco/migration') 
caminho_livro = Path('dados/livros') 

def gerar_migrations(estrategia: str) -> List[Path]:
    return [
        caminho_migrations / 'v1_schema.sql',
        caminho_migrations / 'v2_schema_musica_busca.sql' if estrategia == 'completa' else None,
        caminho_migrations / 'v3_deprecated_schema_rotulo.sql' if estrategia == 'completa' else None,
        caminho_migrations / 'v4_schema_informacoes_musica.sql',
        caminho_migrations / 'v5_schema_biblioteca.sql',
        caminho_migrations / 'v6_dados.sql',
        caminho_migrations / 'v7_deprecated_dados_rotulo.sql' if estrategia == 'completa' else None,
        caminho_migrations / 'v11_rotulos_musica.sql',

        caminho_livro / 'livros_editoras.sql',
    ]

migrations = gerar_migrations(args.estrategia)
migrations_all = gerar_migrations('completa')

for nome_arquivo in arquivos_obra:
    pasta_obra = caminho_obras / nome_arquivo
    if not pasta_obra.is_dir():
        continue

    caminho_informacoes = pasta_obra / 'informacoes.yml'

    with caminho_informacoes.open('r') as arquivo_informacoes:
        informacoes = yaml.safe_load(arquivo_informacoes)

    if not informacoes['disponivel']:
        print(f"Obra \"{informacoes['id_obra']} - {informacoes['titulo']}\" indisponível. Pulando...")
        continue

    if args.obra and args.obra != str(informacoes['id_obra']):
        continue

    livros = [livro for livro in os.listdir(pasta_obra) if (pasta_obra / livro).is_dir()]

    indices: Dict[int, list] = {}
    edicoes_livro: Dict[int, EdicaoLivro] = {}
    secoes_livros: Dict[int, Dict[str, List[int]]] = {}

    for livro in tqdm(livros, desc=f'{informacoes["titulo"]} - Livros'):
        edicao_livro, indices_livro, secoes = parse_livro(pasta_obra / livro)

        if edicao_livro.id_edicao_livro in edicoes_todas_obras:
            raise Exception(f"id_edicao_livro duplicado entre obras: {edicao_livro.id_edicao_livro}")

        edicoes_livro[edicao_livro.id_edicao_livro] = edicao_livro
        secoes_livros[edicao_livro.id_edicao_livro] = secoes
        indices[edicao_livro.id_edicao_livro] = indices_livro

    musicas_elegiveis = set()
    try:
        if livros:
            for indices_livro in indices.values():
                for tupla in indices_livro:
                    if not tupla:
                        continue
                    musicas_elegiveis.add(tupla[0])
    except Exception as e:
        raise e

    # Incluir músicas presentes em informacoes.yml
    musicas_elegiveis = musicas_elegiveis.union(informacoes['musicas'])
    todas_musicas_elegiveis |= musicas_elegiveis
    indices_todas_obras.update(indices)
    edicoes_todas_obras.update(edicoes_livro)
    secoes_todas_obras.update(secoes_livros)

    caminho_banco = destino_obras / f"{informacoes['id_obra']}.sqlite"
    # Remover arquivo se já existir
    origem = Path(caminho_banco)
    if Path(origem).exists():
        origem.unlink()

    musicas: List[Musica] = []

    for nome_arquivo in tqdm(musicas_elegiveis, desc=f'{informacoes["titulo"]} - Músicas'):
        arquivo = caminho_musicas / f"{nome_arquivo}.txt"
        if not arquivo.exists():
            raise Exception(f"Música {arquivo} indexada, mas não encontra-se no catálogo de músicas revisadas (./{caminho_musicas}/)")

        try:
            musica, midias_musica, composicoes_musica = parse_musica_file(arquivo, {})
            musicas.append(musica)
        except Exception as e:
            print(arquivo)
            raise e

    musicas = list(filter(lambda e: not e.is_vazia(), musicas))

    banco = Banco(caminho_banco)
    banco.conectar()
    banco.aplicar_migrations(migrations)

    banco.cadastrar_musicas(musicas)
    banco.cadastrar_indices(indices)
    banco.cadastrar_edicoes_livros(edicoes_livro)
    banco.cadastrar_secoes_livros(secoes_livros)

    if args.estrategia == 'completa':
        banco.testar_scripts()

    obra = Obra(
        id_obra=informacoes['id_obra'],
        titulo=informacoes['titulo'].strip(),
        descricao=informacoes['descricao'].strip(),
        crc32=banco.crc32_sum_musicas(),
        disponivel=informacoes['disponivel'],
    )
    obras.append(obra)

    if args.estrategia == 'completa':
        banco.registrar_obra(obra)
    banco.desconectar()

    if args.estrategia == 'completa':
        verificacao_musicas_persistidas |= set(map(lambda it: it.id_musica, musicas))

# Gerar índice das obras
with open(destino_obras / "obras.json", 'w', encoding='utf-8') as f:
    json.dump([obra.to_json() for obra in obras], f, ensure_ascii=False, indent=4)

# Gerar banco consolidado com todas as obras disponíveis
if not args.obra:
    caminho_banco_todas_obras = destino_obras / 'all.sqlite'
    if caminho_banco_todas_obras.exists():
        caminho_banco_todas_obras.unlink()

    musicas_todas_obras: List[Musica] = []
    for id_musica in tqdm(todas_musicas_elegiveis, desc='Todas as obras - Músicas'):
        arquivo = caminho_musicas / f"{id_musica}.txt"
        if not arquivo.exists():
            raise Exception(f"Música {arquivo} indexada, mas não encontra-se no catálogo de músicas revisadas (./{caminho_musicas}/)")

        try:
            musica, _, _ = parse_musica_file(arquivo, {})
            musicas_todas_obras.append(musica)
        except Exception as e:
            print(arquivo)
            raise e

    musicas_todas_obras = list(filter(lambda e: not e.is_vazia(), musicas_todas_obras))

    banco_todas_obras = Banco(caminho_banco_todas_obras)
    banco_todas_obras.conectar()
    banco_todas_obras.aplicar_migrations(migrations_all)
    banco_todas_obras.cadastrar_musicas(musicas_todas_obras)
    banco_todas_obras.cadastrar_indices(indices_todas_obras)
    banco_todas_obras.cadastrar_edicoes_livros(edicoes_todas_obras)
    banco_todas_obras.cadastrar_secoes_livros(secoes_todas_obras)
    banco_todas_obras.desconectar()

if args.estrategia == 'completa':
    musicas_nao_cadastradas = sorted(verificacao_musicas_txt - verificacao_musicas_persistidas)
    if musicas_nao_cadastradas:
        raise Exception(f"Existem {len(musicas_nao_cadastradas)} músicas que não estão presentes em nenhuma obra: " + ", ".join(map(str, musicas_nao_cadastradas)))


# =========================
# Banco de dados de sugestões de repertório
# =========================

destino_repertorios = Path('api/public/biblioteca/repertorios')
caminho_repertorio_db = destino_repertorios / 'repertorios.sqlite'
caminho_migrations_repertorio = Path('gerador_banco/migration/sugestao_repertorio')


if caminho_repertorio_db.exists():
    caminho_repertorio_db.unlink()

# Ler todos os JSONs de repertório (exceto índices)
# Agrupar por (id_romcal, ano_liturgico) e coletar todas as referências
# Para FESTAS_FIXAS, agrupar tudo em uma única entrada com ano=None
agrupamento: Dict[tuple, dict] = {}

for arquivo_json in sorted(glob.glob(str(destino_repertorios / '**' / '*.json'), recursive=True)):
    nome = os.path.basename(arquivo_json)
    if nome.startswith('indice') or nome == 'indices.json':
        continue

    with open(arquivo_json, 'r', encoding='utf-8') as f:
        entradas = json.load(f)

    for entrada in entradas:
        metadata = entrada.get('metadata', {})
        id_romcal = metadata.get('id_romcal', '')
        ano = metadata.get('ano')  # Pode ser None ou string (A, B, C, etc)
        
        # Para FESTAS_FIXAS, forçar ano=None independente do que vem do JSON
        if id_romcal in FESTAS_FIXAS:
            ano = None
        
        chave = (id_romcal, ano, entrada['titulo'])

        if chave not in agrupamento:
            agrupamento[chave] = {
                'titulo': entrada['titulo'],
                'itens': [],
                'metadata': {},
                'referencias': set(),
                'referencias_por_item': {},  # Novo: rastrear referências por (id, momento)
            }

        # Acumular referências (pode haver múltiplas fontes para a mesma data)
        referencia = metadata.get('referencia', '')
        if referencia:
            agrupamento[chave]['referencias'].add(referencia)

        # Acumular itens sem duplicar (mesmo id + momento = mesmo item)
        # Rastrear referências para cada item
        itens_existentes = {(it['id_musica'], it['momento']) for it in agrupamento[chave]['itens']}
        for item in entrada.get('itens', []):
            chave_item = (item['id_musica'], item['momento'])
            
            if chave_item not in itens_existentes:
                # Primeiro registro deste item: inicializar com a referência atual
                item_copia = item.copy()
                if 'metadata' not in item_copia:
                    item_copia['metadata'] = {}
                else:
                    item_copia['metadata'] = item_copia['metadata'].copy()
                
                # Armazenar referência no metadata do item
                item_copia['metadata']['referencias'] = [referencia] if referencia else []
                agrupamento[chave]['itens'].append(item_copia)
                agrupamento[chave]['referencias_por_item'][chave_item] = set([referencia] if referencia else [])
                itens_existentes.add(chave_item)
            else:
                # Item já existe: adicionar referência se for nova
                if referencia:
                    agrupamento[chave]['referencias_por_item'][chave_item].add(referencia)
                    # Atualizar o item no array com as referências atualizadas
                    for it in agrupamento[chave]['itens']:
                        if (it['id_musica'], it['momento']) == chave_item:
                            if 'metadata' not in it:
                                it['metadata'] = {}
                            it['metadata']['referencias'] = sorted(agrupamento[chave]['referencias_por_item'][chave_item])
                            break

# Ordenar itens por momento litúrgico e inserir no banco
banco_rep = Banco(caminho_repertorio_db)
banco_rep.conectar()
banco_rep.popular_banco(caminho_migrations_repertorio)

cursor = banco_rep.conexao.cursor()

for (id_romcal, ano_liturgico, titulo), dados in sorted(agrupamento.items(), key=lambda x: (x[0][0], x[0][1] or '', x[0][2])):
    # Ordenar itens pela posição litúrgica do momento, mantendo ordem estável dentro do mesmo momento
    dados['itens'].sort(key=lambda it: (Rotulos.ordem_momento(it['momento']), it['id_musica']))

    # Converter referencias de set para list ordenada
    referencias_list = sorted(dados['referencias'])

    itens_json = json.dumps(dados['itens'], ensure_ascii=False)
    dados['metadata']['referencias'] = referencias_list
    metadata_json = json.dumps(dados['metadata'], ensure_ascii=False)
    crc32 = zlib.crc32(itens_json.encode('utf-8')) & 0xFFFFFFFF
    resumo = gerar_resumo(dados['itens'])

    cursor.execute(
        'INSERT INTO sugestao_repertorio (id_romcal, ano_liturgico, titulo, resumo, itens, metadata, crc32) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (id_romcal or None, ano_liturgico or None, dados['titulo'], resumo or None, itens_json, metadata_json, crc32)
    )

banco_rep.conexao.commit()
cursor.close()
banco_rep.desconectar()

print(f"Gerado {caminho_repertorio_db} com {len(agrupamento)} sugestões de repertório.")

# =========================
# Repertório "Geral" (agrupamento de todas as fontes)
# =========================

slug_geral = 'geral'
nome_geral = 'Geral'
destino_geral = destino_repertorios / slug_geral
destino_geral.mkdir(parents=True, exist_ok=True)

# Remove JSONs existentes na pasta geral
for arq in glob.glob(str(destino_geral / '*.json')):
    os.remove(arq)

# Agrupar por nome_arquivo (mesmo padrão de converter/converter_ac)
# Festas fixas: nome_arquivo = id_romcal
# Demais: nome_arquivo = ano_{ano.lower()}_{id_romcal}
por_arquivo_geral = {}
for (id_romcal, ano_liturgico, titulo), dados in agrupamento.items():
    if id_romcal in FESTAS_FIXAS or not ano_liturgico:
        nome_arquivo = id_romcal
    else:
        nome_arquivo = f"ano_{ano_liturgico.lower()}_{id_romcal}"

    entry = por_arquivo_geral.setdefault(nome_arquivo, {
        'id_romcal': id_romcal,
        'repertorios': [],
        'all_ids': [],
        'seen_ids': set(),
    })

    # Ordenar itens
    dados['itens'].sort(key=lambda it: (Rotulos.ordem_momento(it['momento']), it['id_musica']))
    referencias_list = sorted(dados['referencias'])
    dados['metadata']['referencias'] = referencias_list

    # Coletar IDs para prévia
    for it in dados['itens']:
        if not it.get('metadata', {}).get('ignorar', False):
            if it['id_musica'] not in entry['seen_ids']:
                entry['all_ids'].append(it['id_musica'])
                entry['seen_ids'].add(it['id_musica'])

    repertorio = {
        'titulo': dados['titulo'],
        'itens': dados['itens'],
        'metadata': {
            'id_romcal': id_romcal,
            'referencias': referencias_list,
            'ano': ano_liturgico,
        },
    }
    entry['repertorios'].append(repertorio)

itens_indice_geral = []
for nome_arquivo in sorted(por_arquivo_geral.keys()):
    info = por_arquivo_geral[nome_arquivo]
    output_path = destino_geral / f"{nome_arquivo}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(info['repertorios'], f, ensure_ascii=False, indent=2)

    primeiro_titulo = info['repertorios'][0]['titulo']
    itens_indice_geral.append({
        'titulo': primeiro_titulo,
        'slug': nome_arquivo,
        'previa': gerar_previa(info['all_ids']),
        'total_musicas': len(info['all_ids']),
        'crc_32': crc32_arquivo(output_path),
    })

indice_geral_path = destino_repertorios / f'indice-{slug_geral}.json'
with open(indice_geral_path, 'w', encoding='utf-8') as f:
    json.dump({'nome': nome_geral, 'itens': itens_indice_geral}, f, ensure_ascii=False, indent=2)

print(f"[{slug_geral}] {len(por_arquivo_geral)} repertórios gerados em '{destino_geral}'")
print(f"[{slug_geral}] Índice gerado em '{indice_geral_path}'")

# Regenerar indices.json incluindo o 'geral'
gerar_indices()

# Atualizar crc32 do 'geral' no indices.json para ser a soma de todos os crc32 do .sqlite
crc32_geral = sum(
    zlib.crc32(json.dumps(dados['itens'], ensure_ascii=False).encode('utf-8')) & 0xFFFFFFFF
    for dados in agrupamento.values()
)
indices_path = destino_repertorios / 'indices.json'
with open(indices_path, 'r', encoding='utf-8') as f:
    indices_data = json.load(f)
for entrada in indices_data:
    if entrada['slug'] == slug_geral:
        entrada['crc32'] = crc32_geral
        break
with open(indices_path, 'w', encoding='utf-8') as f:
    json.dump(indices_data, f, ensure_ascii=False, indent=2)

# Gerar índice das obras
with open(destino_obras / "obras.json", 'w', encoding='utf-8') as f:
    json.dump([obra.to_json() for obra in obras], f, ensure_ascii=False, indent=4)
