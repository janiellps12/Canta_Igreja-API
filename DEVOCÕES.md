# Orações e terços

Os arquivos ficam separados do catálogo de músicas:

- `dados/oracoes-eucaristicas/`: ordem pelo número no final do arquivo (`...-001.txt`).
- `dados/oracoes/`: orações individuais e subpastas para grupos, em ordem alfabética.
- `dados/tercos/`: terços individuais e subpastas para grupos de mistérios.

Cada TXT usa UTF-8: a primeira linha é o título exibido; as próximas linhas são o texto.
São aceitas as marcações `[b]...[/b]`, `[i]...[/i]` e `[rubrica]...[/rubrica]`.
O nome do arquivo deve usar letras minúsculas sem acentos, números e hífens.
Mantenha o nome do arquivo ao corrigir seu texto para preservar os links existentes.

Uma subpasta vira um grupo automaticamente. O arquivo opcional `informacoes.json`
permite definir `title`, `sort` (`alphabetical` ou `number`) e `order` (lista de nomes
de arquivos sem extensão ou de subpastas). A ordem do Terço Mariano já está definida.

Após o commit e a publicação na Vercel, `python3 build_devotions.py` produz
`/v1/devocoes`. O app baixa o catálogo completo ao abrir e ao voltar à conexão,
preservando a última cópia válida se houver falha. O cache da API pode levar até
alguns minutos para refletir uma nova publicação. Os TXT não entram na busca de cantos.

Conteúdo inicial: PDFs fornecidos pelo responsável pelo app, além das cinco
orações tradicionais do grupo Orações Comuns. As orações básicas dos terços
permanecem apenas indicadas pelos nomes, conforme solicitado.
