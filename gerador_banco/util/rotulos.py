
from dataclasses import dataclass


@dataclass
class RegraRotulos:
    regra: lambda rotulo: bool
    rotulo: str

    def validate(self, rotulos):
        if any(map(lambda it: self.regra(it), rotulos)) and self.rotulo not in rotulos:
            raise ValueError(f'Rótulo "{self.rotulo}" faltando em {rotulos}.')
        
        if len(rotulos) != len(set(rotulos)):
            raise ValueError(f'Rótulo "{self.rotulo}" faltando em {rotulos}.')

regras = [
    RegraRotulos(lambda rotulo: 'Nossa Senhora' in rotulo or rotulo == 'Magnificat', 'Mariano'),
    RegraRotulos(lambda rotulo: rotulo in {'Quinta-feira da Ceia do Senhor', 'Sexta-feira da Paixão do Senhor', 'Vigília Pascal'}, 'Tríduo Pascal'),
    RegraRotulos(lambda rotulo: rotulo in {'Lava-pés'}, 'Quinta-feira da Ceia do Senhor'),
    RegraRotulos(lambda rotulo: rotulo.strip() == '', '<rótulo em branco>'),
]

class Rotulos:
    momentos_liturgicos = {
        'Refrão Meditativo',
        'Entrada',
        'Saudação a Trindade',
        'Ato Penintencial',
        'Aspersão',
        'Glória',
        'Salmo Responsorial',
        'Entronização da Palavra',
        'Aclamação ao Evangelho',
        'Oferendas',
        'Partilha',
        'Santo',
        'Louvação',
        'Paz',
        'Cordeiro de Deus',
        'Comunhão',
        'Pós Comunhão',
        'Final',
    }

    tempo_liturgico = {
        'Advento', 'Tempo do Natal', 'Tempo Comum', 'Quaresma', 'Tríduo Pascal', 'Tempo Pascal'
    }

    semana_santa = {
        'Domingo de Ramos', 'Quinta-feira da Ceia do Senhor', 'Sexta-feira da Paixão do Senhor', 'Vigília Pascal'
    }

    solenidades = {
        'Santa Maria, Mãe de Deus',
        'Epifania do Senhor',
        'São José, esposo da Virgem Santa Maria',
        'Anunciação do Senhor',
        'Segunda-Feira na Oitava da Páscoa',
        'Terça-Feira na Oitava da Páscoa',
        'Quarta-Feira na Oitava da Páscoa',
        'Quinta-Feira na Oitava da Páscoa',
        'Sexta-Feira na Oitava da Páscoa',
        'Sábado na Oitava da Páscoa',
        'Ascensão do Senhor',
        'Domingo de Pentecostes',
        'Santíssima Trindade',
        'Corpus Christi', # Santíssimo Corpo e Sangue de Cristo
        'Natividade de São João Batista',
        'Sagrado Coração de Jesus',
        'São Pedro e São Paulo',
        'Assunção de Nossa Senhora',
        'Nossa Senhora da Conceição Aparecida',
        'Todos os Santos',
        'Finados', # Não é solenidade
        'Nosso Senhor Jesus Cristo, Rei do Universo',
        'Imaculada Conceição de Nossa Senhora',
        'Natal do Senhor',
    }

    festas = {
        'Batismo do Senhor',
        'Conversão de São Paulo, apóstolo',
        'Apresentação do Senhor',
        'Cadeira de São Pedro, apóstolo',
        'Santos Filipe e Tiago, apóstolos',
        'São Matias, apóstolo',
        'Visitação da Nossa Senhora',
        'São Tomé, apóstolo',
        'Nossa Senhora do Carmo',
        'Santa Maria Madalena',
        'São Tiago, apóstolo',
        'Transfiguração do Senhor',
        'Santa Rosa de Lima, virgem',
        'Natividade da Virgem Santa Maria',
        'Exaltação da Santa Cruz',
        'Santos Miguel, Gabriel e Rafael, Arcanjos',
        'São Lucas, evangelista',
        'Santos Simão e Judas Tadeu, apóstolos',
        'Dedicação da Basílica de Latrão',
        'Nossa Senhora de Guadalupe',
        'Santo Estêvão, primeiro mártir',
        'São João, apóstolo e evangelista',
        'Santo André, apóstolo',
        'Sagrada Familia de Jesus, Maria e José',
    }

    sacramentos = {
        'Batismo',
        'Primeira Eucaristia',
        'Crisma',
        'Penintência',
        'Casamento',
        'Ordenação',
        'Unção dos Enfermos',
    }

    musicas_nao_liturgicas = {
        'Não é Santo',
    }

    outros = {
        'Campanha da Fraternidade',
        'Dízimo',
        'Mariano',
        'Missão',
    }

    outros_ritos_e_momentos = {
        'Acendimento da Vela de Coroa do Advento',
        'Adoração ao Santíssimo Sacramento',
        'Adoração da Santa Cruz',
        'Apresentação da Santa Cruz',
        'Imposição das Cinzas',
        'Entrada do Círio Pascal',
        'Lava-pés',
        'Procissão de Ramos',
        'Via-Sacra',
    }

    outros_santos = {
        'Nossa Senhora de Nazaré',
        'Nossa Senhora da Luz',
        'Santa Clara',
        "Santa Teresa D'Ávila",
        'Santa Teresinha do Menino Jesus',
        'Santos Anjos',
        'São Francisco de Assis',
        'São Judas Tadeu',
    }

    o_que_restou = {
        'Exulte',
        'Benção da água',
        'Sequência',
        'Ladainha de Todos os Santos',
        'Magnificat',
        'Não é ato penintencial',
    }

    rotulos_possiveis = (
        momentos_liturgicos
        | tempo_liturgico
        | semana_santa
        | solenidades
        | festas
        | sacramentos
        | musicas_nao_liturgicas
        | outros
        | outros_ritos_e_momentos
        | outros_santos
        | o_que_restou
    )

    # Ordem dos momentos litúrgicos conforme a sequência da Missa.
    # Momentos com a mesma posição na liturgia compartilham o mesmo valor.
    _ordem_momentos: dict[str, int] = {
        # Ritos especiais pré-Missa
        'Acendimento da Vela de Coroa do Advento': 0,
        'Procissão de Ramos':                      1,
        'Entrada do Círio Pascal':                  2,
        'Exulte':                                   3,

        # Ritos Iniciais
        'Entrada':                                  10,
        'Saudação a Trindade':                      11,
        'Ato Penintencial':                         12,
        'Aspersão':                                 12,
        'Não é ato penintencial':                   13,
        'Glória':                                   14,
        'Imposição das Cinzas':                     15,

        # Liturgia da Palavra
        'Refrão Meditativo':                        20,
        'Salmo Responsorial':                       21,
        'Sequência':                                22,
        'Aclamação ao Evangelho':                   23,
        'Entronização da Palavra':                  24,

        # Ritos especiais após a Homilia
        'Lava-pés':                                 30,
        'Adoração da Santa Cruz':                   31,
        'Apresentação da Santa Cruz':               31,
        'Ladainha de Todos os Santos':              32,
        'Benção da água':                           33,

        # Liturgia Eucarística
        'Oferendas':                                40,
        'Partilha':                                 41,
        'Santo':                                    42,
        'Louvação':                                 43,

        # Rito da Comunhão
        'Paz':                                      50,
        'Cordeiro de Deus':                         51,
        'Comunhão':                                 52,
        'Pós Comunhão':                             53,
        'Magnificat':                               54,

        # Ritos Finais
        'Final':                                    60,

        # Momentos extra-litúrgicos / temáticos
        'Via-Sacra':                                70,
        'Adoração ao Santíssimo Sacramento':        71,
    }

    # Valor padrão para momentos não mapeados explicitamente
    _ORDEM_PADRAO = 99

    @staticmethod
    def ordem_momento(momento: str) -> int:
        """Retorna um inteiro que representa a posição do *momento* na liturgia.

        Momentos conhecidos são ordenados conforme a sequência da Missa;
        momentos desconhecidos recebem ``_ORDEM_PADRAO`` (fim da lista).
        """
        return Rotulos._ordem_momentos.get(momento, Rotulos._ORDEM_PADRAO)

    @staticmethod
    def is_valido(rotulo):
        return rotulo in Rotulos.rotulos_possiveis

    @staticmethod
    def validar_rotulos(rotulos):
        rotulos_invalidos = set(rotulos) - Rotulos.rotulos_possiveis
        if rotulos_invalidos:
            raise ValueError(f'Rótulos inválidos: {rotulos_invalidos}')

        for regra in regras:
            regra.validate(rotulos)
