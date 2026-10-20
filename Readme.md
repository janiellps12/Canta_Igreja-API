# Canta Igreja - API

Repositório contendo as músicas presentes no [aplicativo Canta Igreja](https://play.google.com/store/apps/details?id=com.cantaigreja&hl=pt_BR) e no site [https://canta.app](https://canta.app).

As músicas aqui listadas também são disponibilizadas via API, buscando por id
```
https://api.canta.app/musicas/<id>.json
```

Você também pode baixar todas as músicas, divididas em banco de dados
```
# Consulte os banco de dados disponíveis
https://api.canta.app/biblioteca/obras/obras.json

# Baixe um banco de dados em particular
https://api.canta.app/biblioteca/obras/<id do banco>.sqlite
```

Caso você necessite das músicas em outro formato, consulte neste repositório a pasta `/dados/musicas`.

## Desenvolvimento

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python api/main.py
#npx vercel dev

# Validar músicas
# python3 build_api.py --estrategia=completa

# Repertórios
# python3 gerador_banco/repertorios.py converter '{path}/Links APP - Liturgia diária.csv' --nome "Liturgia Diária"
```

## Gerar definições Romcal

Para gerar um arquivo Markdown com as definições do Romcal (chave + nome), use o script `definicoes_romcal.js` presente na raiz do repositório.

Pré-requisitos:

- Node.js (recomendado v16+)
- Dependências do projeto instaladas (`romcal` e `@romcal/calendar.brazil` estão listadas em `package.json`)

Passos:

```bash
# Instalar dependências
npm install

# Executar o script que gera definicoes_romcal.md
node definicoes_romcal.js
```

O script gera o arquivo `definicoes_romcal.md` na raiz do repositório. O arquivo `definicoes_romcal.js` usa sintaxe de módulos ES (`import`); o `package.json` já define `"type": "module"`.

Para customizar o ano ou outras opções, edite `definicoes_romcal.js` antes de executar.

## Regex úteis

* Youtube inválido: `^YouTube:\s(?!h|\n).*`
* Asteriscos soltos: `(?<!\*)\*(?!\*)`
  Obs: atentar-se aos salmos, que tem asterisco no fim solto propositalmente
