"""Testes adicionais de Thompson, equivalência tripla e minimização."""
import itertools
import unittest
from automato import EPSILON, determinizar, thompson
from minimizacao import completar, minimizar
from parser import analisar


def cadeias(alfabeto, maximo):
    for tamanho in range(maximo + 1):
        for letras in itertools.product(alfabeto, repeat=tamanho):
            yield ''.join(letras)


class TestModulos45(unittest.TestCase):
    def test_contagem_thompson_e_casos_manuais(self):
        afn = thompson(analisar('(a|b)*c'))
        self.assertEqual(afn.n_estados, 10)
        self.assertEqual(afn.n_transicoes(), 12)
        vazias = sum(len(saidas.get(EPSILON, ()))
                      for saidas in afn.transicoes.values())
        self.assertEqual(vazias, 9)
        self.assertIsNotNone(afn.reconhece('ababac'))
        self.assertIsNone(afn.reconhece('abab'))

    def test_comparacao_121_cadeias(self):
        afn = thompson(analisar('(a|b)*c'))
        afd = determinizar(afn, ['a', 'b', 'c'])
        minimo = minimizar(afd)
        self.assertEqual(afd.n_estados, 4)
        self.assertEqual(completar(afd).n_estados, 5)
        self.assertEqual(minimo.n_estados, 3)
        textos = list(cadeias('abc', 4))
        self.assertEqual(len(textos), 121)
        aceitas = 0
        for texto in textos:
            resultados = (afn.reconhece(texto), afd.reconhece(texto),
                          minimo.reconhece(texto))
            self.assertEqual(resultados[0], resultados[1], texto)
            self.assertEqual(resultados[1], resultados[2], texto)
            aceitas += resultados[0] is not None
        self.assertEqual(aceitas, 15)

    def test_comparacao_operadores_e_labels(self):
        from automato import unir
        expressoes = ['a', 'ab', 'a|b', 'a*', 'a+', 'a?', 'a(b|c)',
                      '[a-c]', r'\+', '(a|b)*c']
        for exp in expressoes:
            with self.subTest(expressao=exp):
                afn = thompson(analisar(exp))
                afd = determinizar(afn, ['a', 'b', 'c', '+'])
                minimo = minimizar(afd)
                for texto in cadeias('abc+', 3):
                    self.assertEqual(afn.reconhece(texto), afd.reconhece(texto), (exp, texto))
                    self.assertEqual(afd.reconhece(texto), minimo.reconhece(texto), (exp, texto))
        afn = unir([('primeiro', analisar('a')), ('segundo', analisar('b'))])
        afd = determinizar(afn, ['a', 'b'])
        minimo = minimizar(afd)
        self.assertEqual(minimo.reconhece('a'), 'primeiro')
        self.assertEqual(minimo.reconhece('b'), 'segundo')
        self.assertIsNone(minimo.reconhece('c'))

    def test_minimizacao_idempotente(self):
        afd = determinizar(thompson(analisar('a|ab')), ['a', 'b'])
        minimo = minimizar(afd)
        self.assertEqual(minimizar(minimo).n_estados, minimo.n_estados)
        self.assertEqual(minimo.n_transicoes(), minimo.n_estados * 2)

    def test_crescimento_exponencial(self):
        # O sexto símbolo a partir do fim é 'a'.
        exp = '(a|b)*a' + '(a|b)' * 5
        afn = thompson(analisar(exp))
        afd = determinizar(afn, ['a', 'b'])
        minimo = minimizar(afd)
        self.assertGreaterEqual(afd.n_estados, 64)
        self.assertEqual(minimo.n_estados, 64)
        for texto in cadeias('ab', 7):
            self.assertEqual(afn.reconhece(texto), afd.reconhece(texto))
            self.assertEqual(afd.reconhece(texto), minimo.reconhece(texto))


if __name__ == '__main__':
    unittest.main()
