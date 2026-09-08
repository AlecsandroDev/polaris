import unittest

from parser import analisar
from erros import RegexSyntaxError
from padroes import carregar


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


class TestClassesEEscapes(unittest.TestCase):
    def test_classe_vira_alternacao_associada_a_esquerda(self):
        arvore = analisar("[abc]")
        self.assertEqual(arvore.notacao(), "|(|(a, b), c)")

    def test_faixa_se_expande_na_ordem(self):
        arvore = analisar("[a-c]")
        self.assertEqual(arvore.notacao(), "|(|(a, b), c)")

    def test_classe_com_repeticao_nao_duplica_alternativa(self):
        arvore = analisar("[aab]")
        self.assertEqual(arvore.notacao(), "|(a, b)")

    def test_escape_torna_operador_um_simbolo(self):
        # '+' escapado é o sinal da declinação, não o operador "uma ou mais"
        arvore = analisar(r"\+|-")
        self.assertEqual(arvore.notacao(), "|(+, -)")

    def test_classe_nao_fechada_aponta_o_colchete(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("[0-9")
        self.assertEqual(ctx.exception.pos, 0)

    def test_faixa_invertida_e_recusada(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("[9-0]")
        self.assertEqual(ctx.exception.pos, 2)

    def test_barra_no_fim_e_recusada(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("a\\")
        self.assertEqual(ctx.exception.pos, 1)


class TestAlfabetoAmpliado(unittest.TestCase):
    def test_letra_maiuscula_e_digito_sao_simbolos(self):
        self.assertEqual(analisar("M3").notacao(), ".(M, 3)")

    def test_espaco_e_ponto_sao_simbolos(self):
        self.assertEqual(analisar("N 1.").notacao(), ".(.(.(N,  ), 1), .)")

    def test_caractere_fora_do_alfabeto_continua_recusado(self):
        with self.assertRaises(RegexSyntaxError) as ctx:
            analisar("a@b")
        self.assertEqual(ctx.exception.pos, 1)


class TestPadroesDeclarados(unittest.TestCase):
    def test_o_arquivo_de_padroes_e_lido_inteiro(self):
        padroes = carregar()
        self.assertGreaterEqual(len(padroes), 10)
        for nome, expressao, arvore in padroes:
            self.assertTrue(nome and expressao and arvore.notacao())


if __name__ == "__main__":
    unittest.main()
