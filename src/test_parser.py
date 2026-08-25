import unittest

from parser import analisar
from erros import RegexSyntaxError


class TestExemploDaEspecificacao(unittest.TestCase):
    def test_a_ou_b_estrela(self):
        # (a|b)* -> zero ou mais ocorrências de a ou b
        arvore = analisar("(a|b)*")
        self.assertEqual(arvore.notacao(), "*(|(a, b))")


class TestPrecedencia(unittest.TestCase):
    def test_alternacao_tem_a_menor_precedencia(self):
        # a|bc deve ser lido como a|(bc)
        arvore = analisar("a|bc")
        self.assertEqual(arvore.notacao(), "|(a, .(b, c))")

    def test_agrupamento_muda_a_leitura(self):
        # (a|b)c deve ser lido como concatenação na raiz
        arvore = analisar("(a|b)c")
        self.assertEqual(arvore.notacao(), ".(|(a, b), c)")

    def test_estrela_liga_so_no_ultimo_fator(self):
        arvore = analisar("ab*")
        self.assertEqual(arvore.notacao(), ".(a, *(b))")


class TestNucleoDeOperadores(unittest.TestCase):
    def test_mais_vira_concatenacao_com_estrela(self):
        arvore = analisar("a+")
        self.assertEqual(arvore.notacao(), ".(a, *(a))")

    def test_interrogacao_vira_alternacao_com_epsilon(self):
        arvore = analisar("a?")
        self.assertEqual(arvore.notacao(), "|(a, ε)")


class TestErros(unittest.TestCase):
    def test_parentese_nao_fechado(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("a|(")
        self.assertEqual(ctx.exception.pos, 2)

    def test_parentese_sem_abrir(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("a|b)")
        self.assertEqual(ctx.exception.pos, 3)

    def test_operador_estrela_sem_operando(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("*a")
        self.assertEqual(ctx.exception.pos, 0)

    def test_caractere_fora_do_alfabeto(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("a@b")
        self.assertEqual(ctx.exception.pos, 1)


if __name__ == "__main__":
    unittest.main()
