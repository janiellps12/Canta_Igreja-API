---
name: pdf-o-domingo
description: 'Extrai músicas de PDFs do Subsídio Musical "O Domingo" (publicação da Paulus) e cria arquivos no formato padrão do projeto em dados/musicas-a-incluir. Use quando o usuário anexar um PDF do O Domingo e pedir para extrair, importar ou incluir as músicas.'
argument-hint: 'Nome do arquivo PDF (sem a extensão .pdf)'
---

# Extração de Músicas do PDF O Domingo

## Quando Usar

- Usuário anexa um PDF do Subsídio Musical "O Domingo" (Paulus)
- Usuário pede para extrair, importar ou incluir músicas de um PDF
- Usuário menciona "O Domingo", "Subsídio Musical", "Paulus PDF"

## Procedimento

### 1. Identificar o nome do PDF

Perguntar ao usuário o nome exato do arquivo PDF (sem a extensão `.pdf`).  
Esse nome será usado como prefixo nos arquivos gerados.

### 2. Analisar o formato existente

Ler alguns arquivos de `dados/musicas/` para confirmar a estrutura vigente:

```
Índice: 
Título: <título da música>
Rótulos: <ocasião litúrgica; função na missa>
Compositores: <compositor(es)>
Letristas: <letrista(s)>
Musicistas: <musicista(s) / arranjador(es)>
YouTube: 
Partitura: 
CifraClub: 
Tonalidade: <cifra da tonalidade>

<letra formatada em Markdown>
```

**Regras de formatação da letra:**
- Refrão em negrito: `**texto do refrão**`
- Estrofes numeradas: `1. verso` com recuo de 3 espaços nas linhas seguintes
- Repetição: `(2x)` ou notação `||: :||` conforme apresentado no PDF. Caso apareça `(bis)`, interpretar como `(2x)`.
- Asterisco `*` para marcação de pausa salmodia (salmos responsoriais)

### 3. Extrair cada música do PDF

Para cada música apresentada no PDF, coletar:

| Campo | Fonte no PDF |
|-------|-------------|
| **Título** | Cabeçalho colorido da música |
| **Rótulos** | Ocasião (ex: "Santos X; Abertura") |
| **Compositores** | Campo "M.:" ou "L. e M.:" na partitura |
| **Letristas** | Campo "L.:" na partitura |
| **Musicistas** | Campo "Ar.:" (arranjador) na partitura, se houver |
| **Tonalidade** | Cifra inicial da partitura (ex: G, D, F, C) |
| **Letra** | Texto formatado apresentado no PDF |

> **Importante:** Incluir somente as informações explicitamente apresentadas no PDF.  
> Não inferir compositores, letristas ou tonalidade que não estejam claramente indicados.

### 4. Criar os arquivos em `dados/musicas-a-incluir/`

Nomenclatura: `<nome-do-pdf>-<id>.txt`

- `<nome-do-pdf>`: nome do arquivo PDF fornecido pelo usuário (sem `.pdf`)
- `<id>`: número sequencial começando em 1, na ordem em que as músicas aparecem no PDF

Exemplo: para o PDF `o-domingo-santos-pedro-paulo`, os arquivos serão:
- `o-domingo-santos-pedro-paulo-1.txt`
- `o-domingo-santos-pedro-paulo-2.txt`
- etc.

Deixar o campo `Índice:` vazio (será atribuído na inclusão definitiva).  
Deixar `YouTube:`, `Partitura:` e `CifraClub:` vazios.

### 5. Verificar os arquivos criados

Listar os arquivos criados em `dados/musicas-a-incluir/` e confirmar ao usuário com um resumo, apresentado de forma tabular:

```
Músicas extraídas do PDF <nome-do-pdf>:
1. <Título do repertório> — <Rótulos> - <Título da música>
2. <Título do repertório> — <Rótulos> - <Título da música>
...
```

## Mapeamento de Funções da Missa → Rótulos

| Função no PDF      | Rótulo sugerido          |
|--------------------|--------------------------|
| Abertura / Entrada | `<Festa>; Abertura`      |
| Salmo da Vigília   | `<Festa>; Salmo da Vigília; Sl XX(XX)` |
| Salmo Responsorial | `<Festa>; Salmo Responsorial; Sl XX(XX)` |
| Aclamação          | `<Festa>; Aclamação ao Evangelho` |
| Ofertas / Oferendas| `<Festa>; Oferendas`     |
| Comunhão           | `<Festa>; Comunhão`      |
| Final              | `<Festa>; Final`         |

## Notas

- O PDF do "O Domingo" apresenta créditos no formato: `Coral / Letrista / Compositor`  
  Porém os créditos definitivos (L. e M.) estão na partitura impressa e têm precedência.
- Para salmos, o letrista frequentemente é "Lecionário Dominical" ou a referência bíblica.
- O campo `Musicistas` é usado para arranjadores (campo "Ar." na partitura).
