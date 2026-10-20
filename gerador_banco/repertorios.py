"""
Converte arquivos CSV de liturgia em JSONs para a API.

Subcomandos:

  converter     Converte um CSV em JSONs de repertório e gera o indice-<slug>.json
    csv               Path do arquivo CSV
    --nome NOME       Nome legível (ex: "Liturgia Diária") — usado no índice
    --slug SLUG       Slug da pasta (derivado do nome se omitido)

  converter_ac  Converte um CSV no formato Alegre Cantemos e gera o indice-<slug>.json
    csv               Path do arquivo CSV
    --nome NOME       Nome legível da coleção — usado no índice
    --slug SLUG       Slug da pasta (derivado do --nome se omitido)

    Colunas esperadas: Tempo, id_romcal, Data, Data_original, Canto,
                       Ano A, Ano B, Ano C, Comum, Origem

    Diferenças do formato converter:
      - Os IDs por ciclo litúrgico ficam nas colunas Ano A / Ano B / Ano C
        (quando há diferença entre anos) ou em Comum (mesmo canto para todos).
      - Cada id_romcal gera um JSON cujo nome é o próprio id_romcal.
      - O array raiz tem um elemento por (Data × ano). Quando apenas Comum
        está preenchido, gera-se uma entrada com ano vazio em vez de três.

  indices    Lê todos os indice-*.json existentes e gera o indices.json

Exemplos:
    python repertorios.py converter 'Liturgia diária.csv' --nome "Liturgia Diária"
    python repertorios.py converter arquivo.csv --nome "Missas Especiais" --slug missas_especiais
    python repertorios.py converter_ac 'Alegre Cantemos.csv' --nome "Alegre Cantemos" --slug alegre_cantemos
    python repertorios.py indices

Comportamento:
  - Linhas sem id_romcal são ignoradas.
  - Um arquivo JSON é gerado por id_romcal único; o nome do arquivo é o próprio id_romcal
    (a informação do ano litúrgico não compõe o nome do arquivo).
  - A raiz do JSON é um array. Cada elemento corresponde a uma Origem distinta para
    aquele id_romcal, permitindo múltiplos repertórios para a mesma data.

Destino dos JSONs de repertório:
    api/public/biblioteca/repertorios/{slug}/

Estrutura de cada JSON:
    [
        {
            "titulo": "São Pedro e São Paulo",
            "itens": [ { "id", "momento", "metadata": { "indice", "ignorar" } }, ... ],
            "metadata": { "id_romcal", "referencia", "ano" }
        },
        ...
    ]

Índice por coleção:
    api/public/biblioteca/repertorios/indice-{slug}.json
    {
        "nome": "Liturgia Diária",
        "itens": [ { "titulo", "slug", "previa", "total_musicas", "crc_32" }, ... ]
    }

Índice geral:
    api/public/biblioteca/repertorios/indices.json
    [ { "nome": "Liturgia Diária", "slug": "liturgia_diaria", "crc32": ... }, ... ]

Colunas CSV ignoradas (converter): Nome, Letra, Compositor, Letrista, Musicista, Youtube, App
Colunas CSV ignoradas (converter_ac): Tempo, Data_original
"""

import argparse
import csv
import json
import os
import glob
import unicodedata
import re
import zlib
from collections import OrderedDict
from pathlib import Path
from gerador_banco.util.rotulos import Rotulos

BASE_DIR = Path(__file__).resolve().parent.parent
DESTINO_BASE = BASE_DIR / "api" / "public" / "biblioteca" / "repertorios"
CAMINHO_MUSICAS = BASE_DIR / "dados" / "musicas"

# Festas fixas: o nome do arquivo não inclui o ano litúrgico.
FESTAS_FIXAS: frozenset[str] = frozenset({
    "nativity_of_the_lord",
    "holy_family_of_jesus_mary_and_joseph",
    "epiphany_of_the_lord",
    "baptism_of_the_lord",
    "palm_sunday_of_the_passion_of_the_lord",
    "holy_monday",
    "holy_tuesday",
    "holy_wednesday",
    "holy_thursday",
    "friday_of_the_passion_of_the_lord",
    "holy_saturday",
    "mary_mother_of_god",
    "presentation_of_the_lord",
    "most_holy_trinity",
    "most_holy_body_and_blood_of_christ",
    "nativity_of_john_the_baptist",
    "peter_and_paul_apostles",
    "transfiguration_of_the_lord",
    "assumption_of_the_blessed_virgin_mary",
    "exaltation_of_the_holy_cross",
    "our_lady_of_aparecida",
    "all_saints",
    "commemoration_of_all_the_faithful_departed",
    "dedication_of_the_lateran_basilica",
    "immaculate_conception_of_the_blessed_virgin_mary",
})


def slugify(text: str) -> str:
    """Converte texto para snake_case minúsculo sem acentos."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def parse_indice_geral(valor: str) -> list[int]:
    """
    Converte indice_geral em lista de inteiros.
    Suporta formato simples '3017' e múltiplo '3141; 3299'.
    """
    ids = []
    for parte in valor.split(";"):
        parte = parte.strip()
        if parte:
            try:
                ids.append(int(parte))
            except ValueError:
                pass
    return ids


def nome_pasta_do_csv(csv_path: str) -> str:
    """Deriva o slug a partir do nome do arquivo CSV (fallback quando --slug não fornecido)."""
    stem = Path(csv_path).stem
    prefixo = re.match(r"^links?\s+app\s*[-–]\s*", stem, re.IGNORECASE)
    if prefixo:
        stem = stem[prefixo.end():]
    return slugify(stem)


def get_titulo_musica(id_musica: int) -> str | None:
    """Lê o título da música a partir do arquivo .txt correspondente."""
    path = CAMINHO_MUSICAS / f"{id_musica}.txt"
    if not path.exists():
        return None
    for linha in path.read_text(encoding="utf-8").splitlines():
        if linha.startswith("Título: "):
            return linha[len("Título: "):].strip()
    return None


def gerar_previa(ids_em_ordem: list[int]) -> str:
    """Gera string de prévia: primeiros 3 títulos + 'e mais N'."""
    titulos = []
    for id_val in ids_em_ordem:
        titulo = get_titulo_musica(id_val)
        if titulo:
            titulos.append(titulo)
    if not titulos:
        return ""
    if len(titulos) <= 3:
        return ", ".join(titulos)
    return ", ".join(titulos[:3]) + f" e mais {len(titulos) - 3}"


def crc32_arquivo(path: Path) -> int:
    return zlib.crc32(path.read_bytes()) & 0xFFFFFFFF


def validar_momentos_converter(csv_path: str) -> None:
    """Valida coluna 'Momento' do formato converter.
    Levanta ValueError se houver momentos inválidos.
    Omite validação para linhas onde Ignorar=TRUE."""
    erros = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for num_linha, row in enumerate(reader, start=2):  # começa em 2 porque linha 1 é header
            if not row.get("id_romcal", "").strip():
                continue
            # Omite validação se marcado como ignorar
            ignorar = row.get("Ignorar", "").strip().upper() == "TRUE"
            if ignorar:
                continue
            momento = row.get("Momento", "").strip()
            if momento and momento not in Rotulos.rotulos_possiveis:
                erros.append({
                    "linha": num_linha,
                    "id_romcal": row.get("id_romcal", "").strip(),
                    "data": row.get("Data", "").strip(),
                    "origem": row.get("Origem", "").strip(),
                    "momento_invalido": momento,
                })
    if erros:
        msg = f"❌ {len(erros)} momento(s) inválido(s) em {Path(csv_path).name}:\n\n"
        for erro in erros:
            msg += f"  Linha {erro['linha']}: {erro['momento_invalido']!r}\n"
            msg += f"    romcal_key: {erro['id_romcal']}\n"
            msg += f"    data: {erro['data']}\n"
            msg += f"    origem: {erro['origem']}\n\n"
        msg += f"Momentos válidos: {sorted(Rotulos.rotulos_possiveis)}"
        raise ValueError(msg)


def validar_momentos_converter_ac(csv_path: str) -> None:
    """Valida coluna 'Canto' do formato converter_ac.
    Levanta ValueError se houver cantos inválidos."""
    erros = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for num_linha, row in enumerate(reader, start=2):  # começa em 2 porque linha 1 é header
            if not row.get("id_romcal", "").strip():
                continue
            canto = row.get("Canto", "").strip()
            if canto and canto not in Rotulos.rotulos_possiveis:
                erros.append({
                    "linha": num_linha,
                    "id_romcal": row.get("id_romcal", "").strip(),
                    "data": row.get("Data", "").strip(),
                    "tempo": row.get("Tempo", "").strip(),
                    "origem": row.get("Origem", "").strip(),
                    "canto_invalido": canto,
                })
    if erros:
        msg = f"❌ {len(erros)} canto(s) inválido(s) em {Path(csv_path).name}:\n\n"
        for erro in erros:
            msg += f"  Linha {erro['linha']}: {erro['canto_invalido']!r}\n"
            msg += f"    id_romcal: {erro['id_romcal']}\n"
            msg += f"    data: {erro['data']}\n"
            msg += f"    tempo: {erro['tempo']}\n"
            msg += f"    origem: {erro['origem']}\n\n"
        msg += f"Cantos válidos: {sorted(Rotulos.rotulos_possiveis)}"
        raise ValueError(msg)


def converter_csv(csv_path: str, nome: str, slug: str) -> Path:
    """Converte um CSV em JSONs de repertório e gera o arquivo de índice.
    Retorna o path do arquivo de índice gerado."""
    validar_momentos_converter(csv_path)
    
    destino = DESTINO_BASE / slug
    destino.mkdir(parents=True, exist_ok=True)

    # Remove JSONs existentes na pasta destino
    for arq in glob.glob(str(destino / "*.json")):
        os.remove(arq)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Ignora linhas sem id_romcal
    rows = [r for r in rows if r.get("id_romcal", "").strip()]

    # Agrupa por nome de arquivo, preservando a ordem do CSV.
    # Festas fixas: nome_arquivo = id_romcal (sem ano).
    # Demais: nome_arquivo = ano_{ano.lower()}_{id_romcal}.
    # Dentro de cada grupo, sub-agrupa por Origem (repertórios distintos).
    por_arquivo: OrderedDict = OrderedDict()
    for row in rows:
        id_romcal = row["id_romcal"].strip()
        ano = row["Ano Litúrgico"].strip()
        origem = row["Origem"].strip()

        if id_romcal in FESTAS_FIXAS:
            nome_arquivo = id_romcal
        else:
            nome_arquivo = f"ano_{ano.lower()}_{id_romcal}" if ano else id_romcal

        entry = por_arquivo.setdefault(nome_arquivo, {"id_romcal": id_romcal, "origens": OrderedDict()})
        entry["origens"].setdefault(origem, []).append(row)

    itens_indice = []
    arquivos_gerados = 0

    for nome_arquivo, info in por_arquivo.items():
        id_romcal = info["id_romcal"]
        origens_dict = info["origens"]

        # IDs únicos de todas as origens, para o preview do índice
        all_ids: list[int] = []
        seen_ids: set[int] = set()

        # Raiz do JSON = array, um elemento por Origem
        repertorios = []
        for origem, itens_rows in origens_dict.items():
            first_row = itens_rows[0]
            titulo = first_row["Data"].strip()
            ano_liturgico = first_row["Ano Litúrgico"].strip()

            itens = []
            for row in itens_rows:
                ids = parse_indice_geral(row["indice_geral"])
                momento = row["Momento"].strip()
                indice_val = row["índice"].strip() or None
                ignorar = row["Ignorar"].strip().upper() == "TRUE"

                for id_val in ids:
                    itens.append({
                        "id_musica": id_val,
                        "momento": momento,
                        "metadata": {
                            "indice": indice_val,
                            "ignorar": ignorar,
                        },
                    })
                    if id_val not in seen_ids:
                        seen_ids.add(id_val)
                        all_ids.append(id_val)

            if id_romcal in FESTAS_FIXAS:
                ano_liturgico = None  # Festas fixas não têm ano litúrgico específico

            if itens:
                repertorios.append({
                    "titulo": titulo,
                    "itens": itens,
                    "metadata": {
                        "id_romcal": id_romcal,
                        "referencia": origem,
                        "ano": ano_liturgico if ano_liturgico else None,
                    },
                })

        if not repertorios:
            continue

        output_path = destino / f"{nome_arquivo}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(repertorios, f, ensure_ascii=False, indent=2)
        arquivos_gerados += 1

        first_row = list(origens_dict.values())[0][0]
        itens_indice.append({
            "titulo": first_row["Data"].strip(),
            "slug": nome_arquivo,
            "previa": gerar_previa(all_ids),
            "total_musicas": len(all_ids),
            "crc_32": crc32_arquivo(output_path),
        })

    indice_path = DESTINO_BASE / f"indice-{slug}.json"
    with open(indice_path, "w", encoding="utf-8") as f:
        json.dump({"nome": nome, "itens": itens_indice}, f, ensure_ascii=False, indent=2)

    print(f"[{slug}] {arquivos_gerados} repertórios gerados em '{destino}'")
    print(f"[{slug}] Índice gerado em '{indice_path}'")
    return indice_path


def converter_csv_ac(csv_path: str, nome: str, slug: str) -> Path:
    """Converte um CSV no formato Alegre Cantemos em JSONs de repertório e gera o índice.

    Agrupa por (id_romcal, ano_litúrgico) para gerar arquivos separados por ano,
    seguindo o mesmo padrão da função converter():
    - Festas fixas: nome_arquivo = id_romcal
    - Demais: nome_arquivo = ano_<ano>_<id_romcal>

    Cada arquivo JSON contém um array com uma entrada por (Data, Origem).

    Retorna o path do arquivo de índice gerado.
    """
    validar_momentos_converter_ac(csv_path)
    
    destino = DESTINO_BASE / slug
    destino.mkdir(parents=True, exist_ok=True)

    for arq in glob.glob(str(destino / "*.json")):
        os.remove(arq)

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    rows = [r for r in rows if r.get("id_romcal", "").strip()]

    # Agrupa por nome de arquivo (id_romcal com ou sem prefixo de ano),
    # depois por (Data, Origem) para preservar múltiplas origens do mesmo dia.
    por_arquivo: OrderedDict[str, dict] = OrderedDict()
    
    for row in rows:
        id_romcal = row["id_romcal"].strip()
        data = row["Data"].strip()
        origem = row["Origem"].strip()
        
        # Determina se tem entradas por ano (A, B, C)
        tem_ano_a = row.get("Ano A", "").strip()
        tem_ano_b = row.get("Ano B", "").strip()
        tem_ano_c = row.get("Ano C", "").strip()
        tem_comum = row.get("Comum", "").strip()
        
        if id_romcal in FESTAS_FIXAS:
            # Festas fixas: um único arquivo sem separação de ano
            nome_arquivo = id_romcal
            entry = por_arquivo.setdefault(nome_arquivo, {
                "id_romcal": id_romcal,
                "ano": None,
                "origens": OrderedDict()
            })
            entry["origens"].setdefault((data, origem), []).append(row)
        elif tem_ano_a or tem_ano_b or tem_ano_c:
            # Datas móveis com anos diferentes: cria arquivo para cada ano
            for ano_label in ["A", "B", "C"]:
                nome_arquivo = f"ano_{ano_label.lower()}_{id_romcal}"
                entry = por_arquivo.setdefault(nome_arquivo, {
                    "id_romcal": id_romcal,
                    "ano": ano_label,
                    "origens": OrderedDict()
                })
                # Apenas adiciona se tem dados para este ano específico
                id_str = row.get(f"Ano {ano_label}", "").strip() or row.get("Comum", "").strip()
                if id_str:
                    entry["origens"].setdefault((data, origem), []).append(row)
        elif tem_comum:
            # Apenas Comum: um arquivo única sem ano
            nome_arquivo = id_romcal
            entry = por_arquivo.setdefault(nome_arquivo, {
                "id_romcal": id_romcal,
                "ano": None,
                "origens": OrderedDict()
            })
            entry["origens"].setdefault((data, origem), []).append(row)

    itens_indice = []
    arquivos_gerados = 0

    for nome_arquivo, info in por_arquivo.items():
        id_romcal = info["id_romcal"]
        ano_label = info["ano"]
        origens_dict = info["origens"]

        all_ids: list[int] = []
        seen_ids: set[int] = set()

        # Raiz do JSON = array, um elemento por Origem
        repertorios = []
        for (data, origem), itens_rows in origens_dict.items():
            itens = []
            for row in itens_rows:
                # Seleciona o ID apropriado para este ano
                if ano_label:
                    id_str = row.get(f"Ano {ano_label}", "").strip() or row.get("Comum", "").strip()
                else:
                    id_str = row.get("Comum", "").strip()
                
                if id_str:
                    try:
                        id_val = int(id_str)
                    except ValueError:
                        continue
                    itens.append({
                        "id_musica": id_val,
                        "momento": row["Canto"].strip(),
                        "metadata": {"indice": None, "ignorar": False},
                    })
                    if id_val not in seen_ids:
                        seen_ids.add(id_val)
                        all_ids.append(id_val)

            if itens:
                repertorios.append({
                    "titulo": data,
                    "itens": itens,
                    "metadata": {
                        "id_romcal": id_romcal,
                        "referencia": origem,
                        "ano": ano_label if ano_label else None,
                    },
                })

        if not repertorios:
            continue

        output_path = destino / f"{nome_arquivo}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(repertorios, f, ensure_ascii=False, indent=2)
        arquivos_gerados += 1

        first_data = list(origens_dict.keys())[0][0]
        itens_indice.append({
            "titulo": first_data,
            "slug": nome_arquivo,
            "previa": gerar_previa(all_ids),
            "total_musicas": len(all_ids),
            "crc_32": crc32_arquivo(output_path),
        })

    indice_path = DESTINO_BASE / f"indice-{slug}.json"
    with open(indice_path, "w", encoding="utf-8") as f:
        json.dump({"nome": nome, "itens": itens_indice}, f, ensure_ascii=False, indent=2)

    print(f"[{slug}] {arquivos_gerados} repertórios gerados em '{destino}'")
    print(f"[{slug}] Índice gerado em '{indice_path}'")
    return indice_path


def gerar_indices() -> None:
    """Lê todos os indice-*.json existentes e gera o indices.json."""
    entradas = []
    for indice_path in sorted(DESTINO_BASE.glob("indice-*.json")):
        slug = indice_path.stem[len("indice-"):]
        with open(indice_path, encoding="utf-8") as f:
            dados = json.load(f)
        nome = dados.get("nome", slug)
        entradas.append({
            "nome": nome,
            "slug": slug,
            "crc32": crc32_arquivo(indice_path),
        })

    indices_path = DESTINO_BASE / "indices.json"
    with open(indices_path, "w", encoding="utf-8") as f:
        json.dump(entradas, f, ensure_ascii=False, indent=2)
    print(f"indices.json gerado com {len(entradas)} entrada(s) em '{indices_path}'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerador de repertórios para a API")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    # --- subcomando: converter ---
    sub_conv = subparsers.add_parser(
        "converter",
        help="Converte um CSV em JSONs de repertório e gera o indice-<slug>.json",
    )
    sub_conv.add_argument("csv", help="Path do arquivo CSV")
    sub_conv.add_argument(
        "--nome",
        required=True,
        help='Nome legível da coleção (ex: "Liturgia Diária")',
    )
    sub_conv.add_argument(
        "--slug",
        default=None,
        help="Slug da pasta de destino (derivado do --nome se omitido)",
    )

    # --- subcomando: converter_ac ---
    sub_ac = subparsers.add_parser(
        "converter_ac",
        help="Converte um CSV no formato Alegre Cantemos e gera o indice-<slug>.json",
    )
    sub_ac.add_argument("csv", help="Path do arquivo CSV")
    sub_ac.add_argument(
        "--nome",
        required=True,
        help='Nome legível da coleção (ex: "Alegre Cantemos")',
    )
    sub_ac.add_argument(
        "--slug",
        default=None,
        help="Slug da pasta de destino (derivado do --nome se omitido)",
    )

    # --- subcomando: indices ---
    subparsers.add_parser(
        "indices",
        help="Lê todos os indice-*.json existentes e gera o indices.json",
    )

    args = parser.parse_args()

    if args.comando == "converter":
        if not os.path.isfile(args.csv):
            parser.error(f"Arquivo não encontrado: '{args.csv}'")
        slug = args.slug if args.slug else slugify(args.nome)
        converter_csv(args.csv, args.nome, slug)

    elif args.comando == "converter_ac":
        if not os.path.isfile(args.csv):
            parser.error(f"Arquivo não encontrado: '{args.csv}'")
        slug = args.slug if args.slug else slugify(args.nome)
        converter_csv_ac(args.csv, args.nome, slug)

    elif args.comando == "indices":
        gerar_indices()


if __name__ == "__main__":
    main()
