# Sugestões de repertório

Os rascunhos e sugestões publicadas são mantidos pelo painel Gerenciar sugestões do app Cantos das Comunidades em `dados/sugestoes-repertorio.json`.

Cada sugestão inclui id, revision, name, date, year, season, liturgicalColor, status (`draft` ou `published`), items (`songId`, `moment`, `tone`), createdAt, updatedAt e updatedBy (identificador do administrador). Não inclui letras ou repertórios pessoais. Use somente IDs existentes em `dados/musicas/`.

O painel grava pelo servidor autenticado do app, com controle de versão do arquivo no GitHub. A seção pública da página inicial ainda não está ativada; numa etapa futura, a API deverá expor apenas registros `published`.

Rascunhos seguem a visibilidade deste repositório. Evite inserir informações pessoais. Não remova o campo revision ao editar um registro manualmente: altere seu valor para um novo identificador ao modificar o conteúdo, para impedir sobrescrita por edições antigas.
