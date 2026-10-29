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


# Tarefa 3: resultados definidos por leitura manual das expressões,
# independentemente dos resultados produzidos pelo AFD.
# Formato: (expressão, cadeia, aceita?).
CASOS_MANUAIS = [
    ("a", "a", True),
    ("a", "", False),
    ("a", "aa", False),
    ("ab", "ab", True),
    ("ab", "a", False),
    ("ab", "abb", False),
    ("ab", "ac", False),
    ("a|b", "a", True),
    ("a|b", "b", True),
    ("a|b", "", False),
    ("a|b", "ab", False),
    ("a|b", "c", False),
    ("a*", "", True),
    ("a*", "a", True),
    ("a*", "aaaa", True),
    ("a*", "b", False),
    ("a*", "ab", False),
    ("a+", "", False),
    ("a+", "a", True),
    ("a+", "aaa", True),
    ("a+", "aaab", False),
    ("a?", "", True),
    ("a?", "a", True),
    ("a?", "aa", False),
    ("(a|b)*", "", True),
    ("(a|b)*", "abba", True),
    ("(a|b)*", "baba", True),
    ("(a|b)*", "abc", False),
    ("ab*c", "ac", True),
    ("ab*c", "abc", True),
    ("ab*c", "abbbc", True),
    ("ab*c", "ab", False),
    ("ab*c", "abbcb", False),
    ("a(b|c)", "ab", True),
    ("a(b|c)", "ac", True),
    ("a(b|c)", "a", False),
    ("a(b|c)", "abc", False),
    ("[0-2]", "0", True),
    ("[0-2]", "2", True),
    ("[0-2]", "3", False),
    ("[0-2]", "00", False),
    (r"\+", "+", True),
    (r"\+", "", False),
    (r"\+", "++", False),
    (r"\+", "-", False),
    ("a|bc", "a", True),
    ("a|bc", "bc", True),
    ("a|bc", "b", False),
    ("a|bc", "ac", False),
]


class TestSimulacaoAFN(unittest.TestCase):
    def test_casos_resolvidos_a_mao(self):
        for expressao, cadeia, aceita in CASOS_MANUAIS:
            with self.subTest(expressao=expressao, cadeia=cadeia):
                afn = thompson(analisar(expressao), nome="caso")
                esperado = "caso" if aceita else None
                self.assertEqual(afn.reconhece(cadeia), esperado)

    def test_equivalencia_com_afd_nos_casos_manuais(self):
        for expressao, cadeia, _ in CASOS_MANUAIS:
            with self.subTest(expressao=expressao, cadeia=cadeia):
                afn = thompson(analisar(expressao))
                self.assertEqual(afn.reconhece(cadeia),
                                 determinizar(afn).reconhece(cadeia))

    def test_estados_ativos_na_concatenacao(self):
        # Thompson para 'ab': 0 --a--> 1 --ε--> 2 --b--> 3.
        afn = thompson(analisar("ab"), nome="caso")
        nome, passos = afn.simular("ab")
        self.assertEqual(nome, "caso")
        self.assertEqual(passos, [
            (None, frozenset({0})),
            ("a", frozenset({1, 2})),
            ("b", frozenset({3})),
        ])

    def test_palavra_vazia_e_fecho_epsilon(self):
        afn = thompson(analisar("a*"), nome="caso")
        nome, passos = afn.simular("")
        self.assertEqual(nome, "caso")
        self.assertEqual(passos, [(None, frozenset({0, 2, 3}))])
        self.assertIsNone(afn.reconhece("b"))

    def test_sem_destino_recusa(self):
        afn = thompson(analisar("ab"))
        nome, passos = afn.simular("ac")
        self.assertIsNone(nome)
        self.assertEqual(passos[-1], ("c", frozenset()))

    def test_prioridade_na_uniao_de_padroes(self):
        afn = unir([
            ("primeira", analisar("ab")),
            ("segunda", analisar("a(b|c)")),
        ])
        afd = determinizar(afn)
        for cadeia, esperado in [("ab", "primeira"), ("ac", "segunda"),
                                 ("a", None), ("", None), ("abc", None)]:
            with self.subTest(cadeia=cadeia):
                self.assertEqual(afn.reconhece(cadeia), esperado)
                self.assertEqual(afd.reconhece(cadeia), esperado)


class TestPadroesDeclarados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.padroes = carregar()
        cls.afn = unir([(n, a) for n, _, a in cls.padroes])
        cls.afd = determinizar(cls.afn)

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

    def test_afn_reconhece_e_recusa_casos_dos_15_padroes(self):
        for nome, (aceito, recusado) in EXEMPLOS.items():
            with self.subTest(padrao=nome, tipo="aceito"):
                self.assertEqual(self.afn.reconhece(aceito), nome)
            with self.subTest(padrao=nome, tipo="recusado"):
                self.assertIsNone(self.afn.reconhece(recusado))

    def test_afn_e_afd_concordam_no_catalogo(self):
        for aceito, recusado in EXEMPLOS.values():
            for cadeia in (aceito, recusado):
                with self.subTest(cadeia=cadeia):
                    self.assertEqual(self.afn.reconhece(cadeia),
                                     self.afd.reconhece(cadeia))


if __name__ == "__main__":
    unittest.main()
