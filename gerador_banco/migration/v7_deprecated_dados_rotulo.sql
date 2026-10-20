-----------------
-- Rótulos
-----------------
INSERT INTO categoria_rotulo (id_categoria_rotulo, nome, descricao) values
    (1, 'Momento Litúrgico', 'Refere-se às partes da missa'),
    (2, 'Festa Religiosa', 'Músicas específicas para festas religiosas, geralmente dias de Santos'),
    (3, 'Não Litúrgica', 'Músicas não litúrgicas, isto é, que não são adequadas para serem cantandas durante as celebrações conforme o que rege a igreja. As músicas marcadas como não litúrgicas foram explicitamente marcadas para evitar que sejam inseridas em um rito litúrgico erroneamente, de modo a sugerir aos musicistas sua não utilização nos repetórios de missas e celebrações'),
    (4, 'Nossa Senhora', 'Músicas específicas para Maria Nossa Senhora')
;

INSERT INTO rotulo (id_categoria_rotulo, id_rotulo, nome, apelido, descricao) values
    (1, 1, 'Entrada', null, ''),
    (1, 2, 'Aspersão', null, ''),
    (1, 3, 'Ato Penintencial', null, ''),
    (1, 4, 'Glória', null, ''),
    (1, 5, 'Salmo', null, ''),
    (1, 6, 'Aclamação ao Evangelho', null, ''),
    (1, 7, 'Ofertório', null, ''),
    (1, 8, 'Cordeiro de Deus', null, ''),
    (1, 9, 'Santo', null, ''),
    (1, 10, 'Comunhão', null, ''),
    (1, 11, 'Pós Comunhão', null, ''),
    (1, 12, 'Final', null, ''),

    (2, 100, 'São Sebastião', null, 'A festa de São Sebastião ocorre dia 20 de Janeiro e é memória facultativa.'),

    (3, 1000, 'Não considerado como Ato Penintencial', 'Não Ato Penitencial', 'Cânticos de ato penintencial devem possuir "Senhor, tende piedade de nós. Cristo, tende piedade de nós. Senhor, tende piedade de nós". Músicas que não possuem este trecho podem ser cantadas no ato, desde que o celebrante, após o cântico, recite este trecho. Geralmente os celebrantes preferem músicas que já possuam este trecho.'),
    (3, 1001, 'Não considerado como Glória', 'Não Glória', 'Cânticos de Glória devem seguir a letra "<inserir>".'),
    (3, 1002, 'Não considerado como Santo', 'Não Santo', 'Santos devem seguir o hino "Santo santo, Senhor Deus do Universo, os céus e a terra proclamam nossa Glória. Hosana nas alturas. Bendito aquele que vem em nome do Senhor, Hosana nas alturas!'),

    (4, 1100, 'Nossa Senhora Aparecida', 'N.S Aparecida', 'Músicas referenciando Nossa Senhora da Conceição Aparecida, a padroeira do Brasil'),
    (4, 1101, 'Nossa Senhora da Conceição', 'N.S da Conceição', 'Músicas referenciando Nossa Senhora da Conceição'),
    (4, 1102, 'Nossa Senhora de Fátima', 'N.S de Fátima', 'Músicas referenciando Nossa Senhora de Fátima')
;