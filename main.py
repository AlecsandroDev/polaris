"""Comando único: roda uma demonstração e a suíte de testes.

    python3 main.py
"""

import sys
import unittest

sys.path.insert(0, "src")

from parser import analisar
from erros import RegexSyntaxError


EXEMPLOS = ["(a|b)*", "a|bc", "(a|b)c", "a+", "a?"]
EXEMPLOS_INVALIDOS = ["a|(", "a|b)", "*a"]


def demo():
    print("== demonstração ==\n")
    for expressao in EXEMPLOS:
        arvore = analisar(expressao)
        print(f"{expressao!r} -> {arvore.notacao()}")
    print()
    for expressao in EXEMPLOS_INVALIDOS:
        try:
            analisar(expressao)
        except RegexSyntaxError as erro:
            print(erro.formatar(expressao))
            print()


def testes():
    print("== testes ==\n")
    suite = unittest.TestLoader().discover(start_dir="src", pattern="test_*.py", top_level_dir="src")
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    return resultado.wasSuccessful()


if __name__ == "__main__":
    demo()
    ok = testes()
    sys.exit(0 if ok else 1)
