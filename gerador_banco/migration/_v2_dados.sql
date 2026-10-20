-----------------
-- Mídia
-----------------
INSERT INTO tipo_midia (id_tipo_midia, nome, descricao) values
    (1, 'YouTube', 'YouTube é uma plataforma de vídeos. Vídeos de músicas podem apresentar uma versão não oficial.'),
    (2, 'Cifra Club', 'O Cifra Club é uma plataforma online colaborativa criada pela Studio Sol, empresa brasileira também responsável pelas plataformas Palco MP3 e Letras.mus.br (Wikipedia).'),
    (3, 'Partitura', 'Uma partitura é uma representação escrita de música padronizada mundialmente (Wikipedia). Partituras são coletadas da internet e podem apresentar erros.')
;

-----------------
-- Composição
-----------------
INSERT INTO tipo_composicao (id_tipo_composicao, nome, descricao) values
    (1, 'Composição', 'Contribuição realizada na letra e também na melodia da música. Caso não seja possível identificar onde a contribuição foi feita, é informado como "Composição"'),
    (2, 'Letra', 'Contribuição realizada na letra.'),
    (3, 'Melodia', 'Contribuição realizada na melodia.')
;
