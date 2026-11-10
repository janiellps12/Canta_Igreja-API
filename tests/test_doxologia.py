import json
import sqlite3
import unittest
from pathlib import Path
from gerador_banco.util.rotulos import Rotulos
from gerador_banco.model.musica import Musica


class DoxologiaTest(unittest.TestCase):
    def test_rotulo_valido_e_ordenado_antes_do_cordeiro(self):
        self.assertIn('Doxologia', Rotulos.momentos_liturgicos)
        self.assertTrue(Rotulos.is_valido('Doxologia'))
        Rotulos.validar_rotulos(['Doxologia', 'Tempo Comum'])
        self.assertLess(Rotulos.ordem_momento('Doxologia'), Rotulos.ordem_momento('Cordeiro de Deus'))

    def test_json_e_banco_aceitam_e_preservam_o_rotulo(self):
        musica = Musica(999999, 'Amém de teste', 'Letra de teste', '', [], [], ['Doxologia', 'Tempo Comum'], Path('999999.txt'))
        musica.validate()
        self.assertEqual(musica.to_json()['rotulos'], ['Doxologia', 'Tempo Comum'])
        with sqlite3.connect(':memory:') as db:
            for filename in ['v1_schema.sql', 'v4_schema_informacoes_musica.sql', 'v5_schema_biblioteca.sql', 'v11_rotulos_musica.sql']:
                db.executescript((Path(__file__).parents[1] / 'gerador_banco/migration' / filename).read_text(encoding='utf-8'))
            db.execute('insert into musica values (?, ?, ?, ?, ?, ?, ?)', musica.to_tuple())
            saved = db.execute('select rotulos from musica where id_musica=?', (musica.id_musica,)).fetchone()[0]
            self.assertEqual(json.loads(saved), ['Doxologia', 'Tempo Comum'])


if __name__ == '__main__':
    unittest.main()
