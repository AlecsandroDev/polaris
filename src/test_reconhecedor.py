"""Testes do componente separado: a tabela em disco basta para reconhecer."""

import json
import os
import tempfile
import unittest

from automato import determinizar, unir
from medir import gravar_tabela
from padroes import carregar
from reconhecedor import Reconhecedor

LINHA = "Nebulosa de Orion    M42     NGC 1976    05 35 17.3 -05 23 28"


class TestIdaEVolta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        afd = determinizar(unir([(n, a) for n, _, a in carregar()]))
        cls.afd = afd
        with tempfile.TemporaryDirectory() as pasta:
            caminho = gravar_tabela(afd, os.path.join(pasta, "afd.json"))
            with open(caminho, encoding="utf-8") as arquivo:
                cls.tabela = json.load(arquivo)
        cls.reconhecedor = Reconhecedor(cls.tabela)

    def test_a_tabela_preserva_o_numero_de_estados(self):
        self.assertEqual(self.reconhecedor.n_estados, self.afd.n_estados)

    def test_reconhece_a_partir_da_tabela_sozinha(self):
        self.assertEqual(self.reconhecedor.maior_casamento("NGC 1976", 0), (8, "ngc"))

    def test_varre_uma_linha_de_catalogo(self):
        achados = [(nome, trecho) for _, _, nome, trecho in self.reconhecedor.varrer(LINHA)]
        self.assertEqual(achados, [
            ("messier", "M42"),
            ("ngc", "NGC 1976"),
            ("sexagesimal", "05 35 17.3 -05 23 28"),
        ])

    def test_maior_casamento_prefere_o_trecho_mais_longo(self):
        # 'NGC 1976' inteiro, e não o 'NGC 1' que já seria aceito
        self.assertEqual(self.reconhecedor.maior_casamento("NGC 1976 e mais", 0), (8, "ngc"))

    def test_texto_sem_designacao_nao_produz_achado(self):
        self.assertEqual(self.reconhecedor.varrer("objeto ainda não catalogado"), [])


if __name__ == "__main__":
    unittest.main()
