import unittest

from automato import determinizar, thompson, unir
from padroes import carregar
from parser import analisar

# Uma designação ou coordenada real por padrão declarado, e uma quase-forma
# que precisa ser recusada.
EXEMPLOS = {
    "messier":     ("M31",                             "M3100"),
    "ngc":         ("NGC 1976",                        "NGC"),
    "ic":          ("IC 434",                          "IC434"),
    "hd":          ("HD 209458",                       "HD "),
    "hip":         ("HIP 27989",                       "HIP27989"),
    "hr":          ("HR 2061",                         "HR 20a1"),
    "tycho":       ("TYC 1234-5678-1",                 "TYC 1234-5678"),
    "bayer":       ("alf Ori",                         "alf ori"),
    "flamsteed":   ("61 Cyg",                          "61 C"),
    "gaia":        ("Gaia DR3 4116249658590184064",    "Gaia DR3"),
    "twomass":     ("2MASS J05551028+0724255",         "2MASS J05551028 0724255"),
    "sdss":        ("SDSS J000000.00+000000.0",        "SDSS J000000.00+000000"),
    "sexagesimal": ("05 35 17.3 -05 23 28",            "05 35 17.3 05 23 28"),
    "hmsdms":      ("05h35m17.3s +22d00m52s",          "05h35m17.3 +22d00m52s"),
    "decimal":     ("83.822 -5.391",                   "83 -5.391"),
}


class TestThompson(unittest.TestCase):
    def test_simbolo_tem_dois_estados(self):
        self.assertEqual(thompson(analisar("a")).n_estados, 2)

    def test_concatenacao_nao_acrescenta_estado(self):
        # dois símbolos, ligados por ε: 2 + 2, nada a mais
        self.assertEqual(thompson(analisar("ab")).n_estados, 4)

    def test_alternacao_acrescenta_dois_estados(self):
        self.assertEqual(thompson(analisar("a|b")).n_estados, 6)

    def test_estrela_acrescenta_dois_estados(self):
        self.assertEqual(thompson(analisar("a*")).n_estados, 4)

    def test_mais_duplica_a_subarvore(self):
        # a+ vira aa*, então custa o dobro de a, mais os dois estados da estrela
        self.assertEqual(thompson(analisar("a+")).n_estados, 6)


class TestDeterminizacao(unittest.TestCase):
    def test_reconhece_o_exemplo_da_especificacao(self):
        afd = determinizar(thompson(analisar("(a|b)*")))
        for aceito in ("", "a", "b", "abba"):
            self.assertIsNotNone(afd.reconhece(aceito), aceito)
        self.assertIsNone(afd.reconhece("c"))

    def test_transicao_ausente_recusa(self):
        afd = determinizar(thompson(analisar("ab")))
        self.assertIsNone(afd.reconhece("aa"))
        self.assertIsNone(afd.reconhece("a"))
        self.assertIsNone(afd.reconhece("abb"))

    def test_a_uniao_respeita_a_ordem_de_declaracao(self):
        # as duas formas casam com 'ab'; vence a declarada primeiro
        afn = unir([("primeira", analisar("ab")), ("segunda", analisar("a[a-b]"))])
        self.assertEqual(determinizar(afn).reconhece("ab"), "primeira")


class TestPadroesDeclarados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.padroes = carregar()
        cls.afd = determinizar(unir([(n, a) for n, _, a in cls.padroes]))

    def test_todos_os_padroes_tem_exemplo(self):
        self.assertEqual({n for n, _, _ in self.padroes}, set(EXEMPLOS))

    def test_cada_padrao_reconhece_o_seu_exemplo(self):
        for nome, _, arvore in self.padroes:
            aceito, _ = EXEMPLOS[nome]
            afd = determinizar(thompson(arvore, nome))
            self.assertEqual(afd.reconhece(aceito), nome, f"{nome}: {aceito!r}")

    def test_cada_padrao_recusa_a_quase_forma(self):
        for nome, _, arvore in self.padroes:
            _, recusado = EXEMPLOS[nome]
            afd = determinizar(thompson(arvore, nome))
            self.assertIsNone(afd.reconhece(recusado), f"{nome}: {recusado!r}")

    def test_o_reconhecedor_unico_classifica_cada_exemplo(self):
        for nome, (aceito, _) in EXEMPLOS.items():
            self.assertEqual(self.afd.reconhece(aceito), nome, f"{aceito!r}")


if __name__ == "__main__":
    unittest.main()
