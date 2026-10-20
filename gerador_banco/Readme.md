# Gerador de banco

Facilitador para gerar arquivo do banco de dados

## Instalar dependências

Na pasta `gerador_banco`, execute:

```shell
# Criar ambiente virtual. Necessário executar uma única vez
python3 -m venv venv
# Ativar ambiente
source venv/bin/activate
# Instalar bibliotecas dependências do projeto. Necessário executar uma única vez
pip install -r requirements.txt
```

## Converter repertórios

O script `repertorios.py` converte arquivos CSV de liturgia em JSONs para a API.

### Subcomando: converter (formato genérico)

Converte um CSV com colunas `id_romcal`, `Origem`, `Data`, `Canto`, `Ano Litúrgico`, `indice_geral`, `índice`, `Ignorar` em JSONs de repertório.

```bash
# Sintaxe
python repertorios.py converter <arquivo.csv> --nome "Nome da Coleção" [--slug slug_destino]

# Exemplo
python repertorios.py converter 'Liturgia diária.csv' --nome "Liturgia Diária"
python repertorios.py converter 'Links APP - Salmos.csv' --nome "Leituras"
python repertorios.py converter '/Users/paulomateus/Downloads/Links APP - O Domingo - Liturgia Diária - Paulus.csv' --nome "O Domingo"

# Com slug customizado
python repertorios.py converter arquivo.csv --nome "Missas Especiais" --slug missas_especiais
```

**Comportamento:**
- Gera um arquivo JSON por `id_romcal` único
- A raiz de cada JSON é um array com uma entrada por `Origem` distinta
- Destino: `api/public/biblioteca/repertorios/{slug}/`
- Cria índice: `api/public/biblioteca/repertorios/indice-{slug}.json`

### Subcomando: converter_ac (formato Alegre Cantemos)

Converte um CSV no formato Alegre Cantemos com colunas `Tempo`, `romcal_key`, `Data`, `Canto`, `Ano A`, `Ano B`, `Ano C`, `Comum`, `Origem`.

```bash
# Sintaxe
python repertorios.py converter_ac <arquivo.csv> --nome "Nome da Coleção" [--slug slug_destino]

# Exemplo
python repertorios.py converter_ac 'Alegre Cantemos.csv' --nome "Alegre Cantemos" --slug alegre_cantemos
```

**Comportamento:**
- Gera um arquivo JSON por `romcal_key` único (nome do arquivo = `romcal_key`)
- Quando cantos variam entre ciclos A/B/C → cria 3 entradas (uma por ano)
- Quando só `Comum` está preenchido → cria 1 entrada com `"ano": ""`
- Destino: `api/public/biblioteca/repertorios/{slug}/`
- Cria índice: `api/public/biblioteca/repertorios/indice-{slug}.json`

### Subcomando: indices

Lê todos os `indice-*.json` existentes e gera o `indices.json` consolidado.

```bash
python repertorios.py indices
```

**Resultado:**
- Cria/atualiza: `api/public/biblioteca/repertorios/indices.json`
- Consolida metadados de todas as coleções

### Exemplo completo: processar novo repertório

```bash
cd gerador_banco

# 1. Converter um novo CSV para repertório
python repertorios.py converter_ac 'novo_repertorio.csv' --nome "Novo Repertório" --slug novo_repertorio

# 2. Gerar o indices.json consolidado
python repertorios.py indices
```

## Criar banco

Na raiz do projeto, execute:

```shell
# Criar novo banco
python script.py output/cantaIgreja.db
# Criar link dos asset
#cd app/
#npx react-native-asset@latest
```

## Verificar duplicidades

```bash
cd gerador_banco
pip install -r requirements-ai.txt
python duplicidades.py
cd ..

docker run -it --rm -p 8888:8888 -v "${PWD}":/home/jovyan/work quay.io/jupyter/datascience-notebook:2023-11-17
```
